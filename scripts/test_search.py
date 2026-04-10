#!/usr/bin/env python3
"""
Script para ejecutar búsquedas de prueba en GitHub y guardar resultados completos.
Genera un archivo JSON con todas las relaciones: repos, usuarios, contribuidores, etc.

Uso:
    python scripts/test_search.py --all           # Ejecuta todas las búsquedas
    python scripts/test_search.py --name "Java"   # Ejecuta búsqueda específica
    python scripts/test_search.py --query "language:python" --limit 5  # Búsqueda directa
"""

import sys
import os
import argparse
import json
import re
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.github_client import github_client


COUNTRY_MAP = {
    "united states": "United States", "usa": "United States", "us": "United States",
    "uk": "United Kingdom", "united kingdom": "United Kingdom", "england": "United Kingdom",
    "germany": "Germany", "deutschland": "Germany",
    "france": "France", "españa": "Spain", "spain": "Spain",
    "italy": "Italy", "italia": "Italy",
    "portugal": "Portugal", "brasil": "Brazil", "brazil": "Brazil",
    "mexico": "Mexico", "méxico": "Mexico",
    "argentina": "Argentina", "chile": "Chile", "colombia": "Colombia",
    "peru": "Peru", "perú": "Peru", "venezuela": "Venezuela",
    "canada": "Canada", "australia": "Australia",
    "japan": "Japan", "china": "China", "india": "India",
    "russia": "Russia", "russian federation": "Russia",
    "netherlands": "Netherlands", "poland": "Poland", "sweden": "Sweden",
    "norway": "Norway", "denmark": "Denmark", "finland": "Finland",
    "belgium": "Belgium", "switzerland": "Switzerland", "austria": "Austria",
    "ireland": "Ireland", "singapore": "Singapore", "hong kong": "Hong Kong",
    "south korea": "South Korea", "korea": "South Korea", "taiwan": "Taiwan",
    "indonesia": "Indonesia", "malaysia": "Malaysia", "thailand": "Thailand",
    "vietnam": "Vietnam", "philippines": "Philippines",
    "egypt": "Egypt", "south africa": "South Africa", "nigeria": "Nigeria",
    "israel": "Israel", "uae": "United Arab Emirates", "dubai": "United Arab Emirates",
    "turkey": "Turkey", "pakistan": "Pakistan", "bangladesh": "Bangladesh",
    "new zealand": "New Zealand", "netherlands": "Netherlands",
    "czech republic": "Czech Republic", "czechia": "Czech Republic",
    "hungary": "Hungary", "romania": "Romania", "bulgaria": "Bulgaria",
    "greece": "Greece", "ukraine": "Ukraine", "croatia": "Croatia",
}


def extract_country(location):
    if not location:
        return None
    location_lower = location.lower().strip()
    for key, value in COUNTRY_MAP.items():
        if key in location_lower:
            return value
    return location


def extract_city(location):
    if not location:
        return None
    parts = [p.strip() for p in location.split(",")]
    if len(parts) > 1:
        return parts[0]
    return None


SOCIAL_PATTERNS = {
    "linkedin": [
        r'linkedin\.com/in/([a-zA-Z0-9_-]+)',
        r'linkedin\.com/company/([a-zA-Z0-9_-]+)',
        r'linkedin\.com/([a-zA-Z0-9_-]+)',
    ],
    "twitter": [
        r'twitter\.com/([a-zA-Z0-9_-]+)',
        r'x\.com/([a-zA-Z0-9_-]+)',
    ],
    "instagram": [
        r'instagram\.com/([a-zA-Z0-9_.]+)',
    ],
    "facebook": [
        r'facebook\.com/([a-zA-Z0-9_.]+)',
        r'fb\.com/([a-zA-Z0-9_.]+)',
    ],
    "youtube": [
        r'youtube\.com/@([a-zA-Z0-9_-]+)',
        r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
        r'youtube\.com/user/([a-zA-Z0-9_-]+)',
    ],
    "reddit": [
        r'reddit\.com/user/([a-zA-Z0-9_-]+)',
        r'u/([a-zA-Z0-9_-]+)',
    ],
    "devto": [
        r'dev\.to/([a-zA-Z0-9_-]+)',
    ],
    "medium": [
        r'medium\.com/@([a-zA-Z0-9_-]+)',
        r'medium\.com/([a-zA-Z0-9_-]+)',
    ],
    "stackoverflow": [
        r'stackoverflow\.com/users/(\d+)',
    ],
    "gitlab": [
        r'gitlab\.com/([a-zA-Z0-9_-]+)',
    ],
    "bitbucket": [
        r'bitbucket\.org/([a-zA-Z0-9_-]+)',
    ],
    "discord": [
        r'discord\.gg/([a-zA-Z0-9_-]+)',
    ],
    "telegram": [
        r't\.me/([a-zA-Z0-9_-]+)',
        r'telegram\.me/([a-zA-Z0-9_-]+)',
    ],
}


def extract_social_links(blog, html_url, twitter_username=None):
    social_links = {}
    
    texts_to_search = [blog, html_url]
    if twitter_username:
        texts_to_search.append(f"https://twitter.com/{twitter_username}")
    
    for platform, patterns in SOCIAL_PATTERNS.items():
        for text in texts_to_search:
            if not text:
                continue
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    full_url = match.group(0)
                    if not full_url.startswith('http'):
                        if 'linkedin' in platform:
                            full_url = f"https://linkedin.com/{match.group(1)}"
                        elif 'twitter' in platform or 'x.com' in pattern:
                            full_url = f"https://twitter.com/{match.group(1)}"
                        elif 'instagram' in platform:
                            full_url = f"https://instagram.com/{match.group(1)}"
                        elif 'facebook' in platform:
                            full_url = f"https://facebook.com/{match.group(1)}"
                        elif 'youtube' in platform:
                            full_url = f"https://youtube.com/{match.group(0).split('youtube.com/')[1]}"
                        elif 'reddit' in platform:
                            if 'u/' in pattern:
                                full_url = f"https://reddit.com/u/{match.group(1)}"
                            else:
                                full_url = f"https://reddit.com/user/{match.group(1)}"
                        elif 'devto' in platform:
                            full_url = f"https://dev.to/{match.group(1)}"
                        elif 'medium' in platform:
                            full_url = f"https://medium.com/{match.group(1)}"
                        elif 'stackoverflow' in platform:
                            full_url = f"https://stackoverflow.com/users/{match.group(1)}"
                        elif 'gitlab' in platform:
                            full_url = f"https://gitlab.com/{match.group(1)}"
                        elif 'bitbucket' in platform:
                            full_url = f"https://bitbucket.org/{match.group(1)}"
                        elif 'discord' in platform:
                            full_url = f"https://discord.gg/{match.group(1)}"
                        elif 'telegram' in platform:
                            full_url = f"https://t.me/{match.group(1)}"
                    
                    social_links[platform] = full_url
                    break
            if platform in social_links:
                break
    
    return social_links


def extract_all_urls(text):
    if not text:
        return []
    
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    
    return [url.rstrip('.,;:!?') for url in urls]


def build_contact_info(user_details, social_links):
    contact_info = {
        "email": user_details.get("email"),
        "phone": None,
        "location": user_details.get("location"),
        "country": extract_country(user_details.get("location", "")),
        "city": extract_city(user_details.get("location", "")),
        "hireable": user_details.get("hireable", False),
        "website": user_details.get("blog") if user_details.get("blog") else None,
        "social_links": social_links if social_links else None,
        "additional_urls": []
    }
    
    blog = user_details.get("blog", "")
    if blog:
        all_urls = extract_all_urls(blog)
        social_platforms = set(SOCIAL_PATTERNS.keys())
        for url in all_urls:
            url_lower = url.lower()
            if not any(platform in url_lower for platform in social_platforms):
                if url not in [contact_info.get("website")]:
                    contact_info["additional_urls"].append({
                        "url": url,
                        "type": "website_or_other"
                    })
    
    contact_info = {k: v for k, v in contact_info.items() if v is not None and v != []}
    
    if "additional_urls" in contact_info and not contact_info["additional_urls"]:
        del contact_info["additional_urls"]
    
    return contact_info


OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def print_separator(char="=", length=80):
    print(char * length)


def print_header(text):
    print_separator()
    print(f"  {text}")
    print_separator()


def calculate_scores(data):
    scores = {
        "users": {},
        "repositories": {},
        "technologies": {}
    }
    
    for repo_id, repo in data["repositories"].items():
        popularity = repo.get("stars", 0) * 2 + repo.get("forks", 0)
        engagement = repo.get("open_issues", 0) + repo.get("watchers", 0)
        scores["repositories"][repo_id] = {
            "popularity_score": popularity,
            "engagement_score": engagement,
            "quality_score": popularity / max(repo.get("forks", 1), 1)
        }
    
    for user_id, user in data["users"].items():
        social = user.get("social_stats", {})
        followers = social.get("followers", 0)
        public_repos = social.get("public_repos", 0)
        
        repo_stars = 0
        for rid, rdata in data.get("user_repositories", {}).get(user_id, {}).get("repo_details", {}).items():
            repo_stars += rdata.get("stars", 0)
        
        tech_diversity = len(data.get("relationships", {}).get("user_to_technologies", {}).get(user_id, {}).get("languages", {}))
        
        contribution_count = len(data.get("relationships", {}).get("user_to_contributed_repos", {}).get(user_id, {}).get("contributed_repos", []))
        
        contact = user.get("contact_info", {})
        social_links = contact.get("social_links", {}) if contact else {}
        
        has_linkedin = "linkedin" in social_links if social_links else False
        has_email = contact.get("email") is not None if contact else False
        has_location = contact.get("location") is not None if contact else False
        has_other_social = len(social_links) > 0 if social_links else False
        
        contact_score = sum([has_linkedin, has_email, has_location, has_other_social])
        
        scores["users"][user_id] = {
            "influence_score": followers + repo_stars,
            "activity_score": public_repos + contribution_count,
            "tech_diversity": tech_diversity,
            "community_score": contribution_count,
            "contact_completeness": contact_score,
            "social_links_found": list(social_links.keys()) if social_links else []
        }
    
    for tech_name, tech_data in data.get("technologies", {}).items():
        scores["technologies"][tech_name] = {
            "popularity_score": tech_data.get("repositories_count", 0) * 10 + tech_data.get("users_count", 0),
            "total_repos": tech_data.get("repositories_count", 0),
            "total_users": tech_data.get("users_count", 0)
        }
    
    return scores


def fetch_user_details(username):
    try:
        return github_client.get_user(username)
    except Exception as e:
        print(f"      ⚠️  Error obteniendo detalles de {username}: {e}")
        return {}


def fetch_user_repos(username):
    try:
        return github_client.get_user_repos(username)
    except Exception as e:
        print(f"      ⚠️  Error obteniendo repos de {username}: {e}")
        return []


def process_repository(repo_data, config, data):
    repo_id = str(repo_data["id"])
    
    print(f"\n  📦 Procesando: {repo_data['full_name']}")
    
    repo_info = {
        "github_id": repo_data["id"],
        "name": repo_data["name"],
        "full_name": repo_data["full_name"],
        "owner_login": repo_data["owner"]["login"],
        "description": repo_data.get("description"),
        "stars": repo_data.get("stargazers_count", 0),
        "forks": repo_data.get("forks_count", 0),
        "language": repo_data.get("language"),
        "url": repo_data.get("html_url"),
        "created_at": repo_data.get("created_at"),
        "updated_at": repo_data.get("updated_at"),
        "pushed_at": repo_data.get("pushed_at"),
        "open_issues": repo_data.get("open_issues_count", 0),
        "watchers": repo_data.get("watchers_count", 0),
        "topics": repo_data.get("topics", []),
        "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
        "homepage": repo_data.get("homepage")
    }
    
    data["repositories"][repo_id] = repo_info
    
    if repo_info["language"]:
        if repo_info["language"] not in data["technologies"]:
            data["technologies"][repo_info["language"]] = {
                "name": repo_info["language"],
                "repositories_count": 0,
                "users_count": 0
            }
        data["technologies"][repo_info["language"]]["repositories_count"] += 1
        
        if repo_info["language"] not in data["relationships"]["tech_to_repos"]:
            data["relationships"]["tech_to_repos"][repo_info["language"]] = {"repo_ids": []}
        data["relationships"]["tech_to_repos"][repo_info["language"]]["repo_ids"].append(repo_id)
    
    if config.get("fetch_contributors", False):
        owner, repo_name = repo_data["full_name"].split("/")
        contributors_limit = config.get("contributors_limit", 5)
        
        print(f"     👥 Obteniendo top {contributors_limit} contribuidores...")
        try:
            contributors = github_client.get_repo_contributors(owner, repo_name)
            contributors = contributors[:contributors_limit]
            
            data["relationships"]["repo_to_contributors"][repo_id] = {"contributors": []}
            
            for contrib in contributors:
                contrib_login = contrib.get("login")
                contrib_id = str(contrib.get("id", 0))
                contrib_count = contrib.get("contributions", 0)
                
                print(f"        - {contrib_login} ({contrib_count} contribuciones)")
                
                data["relationships"]["repo_to_contributors"][repo_id]["contributors"].append({
                    "user_github_id": contrib.get("id", 0),
                    "contributions": contrib_count,
                    "user_login": contrib_login
                })
                
                if contrib_id not in data["users"]:
                    print(f"          📤 Obteniendo perfil de {contrib_login}...")
                    user_details = fetch_user_details(contrib_login)
                    
                    if user_details:
                        location = user_details.get("location", "")
                        country = extract_country(location)
                        
                        social_links = extract_social_links(
                            user_details.get("blog", ""),
                            user_details.get("html_url", ""),
                            user_details.get("twitter_username")
                        )
                        
                        contact_info = build_contact_info(user_details, social_links)
                        
                        data["users"][contrib_id] = {
                            "github_id": user_details.get("id"),
                            "login": user_details.get("login"),
                            "name": user_details.get("name"),
                            "avatar_url": user_details.get("avatar_url"),
                            "html_url": user_details.get("html_url"),
                            "bio": user_details.get("bio"),
                            "company": user_details.get("company"),
                            "type": user_details.get("type", "User"),
                            "created_at": user_details.get("created_at"),
                            "updated_at": user_details.get("updated_at"),
                            "contact_info": contact_info,
                            "social_stats": {
                                "followers": user_details.get("followers", 0),
                                "following": user_details.get("following", 0),
                                "public_repos": user_details.get("public_repos", 0),
                                "public_gists": user_details.get("public_gists", 0)
                            }
                        }
                        
                        if contrib_id not in data["relationships"]["user_to_contributed_repos"]:
                            data["relationships"]["user_to_contributed_repos"][contrib_id] = {
                                "contributed_repos": [],
                                "contribution_counts": {}
                            }
                        data["relationships"]["user_to_contributed_repos"][contrib_id]["contributed_repos"].append(int(repo_id))
                        data["relationships"]["user_to_contributed_repos"][contrib_id]["contribution_counts"][repo_id] = contrib_count
                        
                        if country:
                            if country not in data["relationships"]["country_to_users"]:
                                data["relationships"]["country_to_users"][country] = {
                                    "user_ids": [],
                                    "count": 0
                                }
                            if int(contrib_id) not in data["relationships"]["country_to_users"][country]["user_ids"]:
                                data["relationships"]["country_to_users"][country]["user_ids"].append(int(contrib_id))
                                data["relationships"]["country_to_users"][country]["count"] = len(data["relationships"]["country_to_users"][country]["user_ids"])
                
                if config.get("fetch_user_repos", True):
                    print(f"          📚 Obteniendo repositorios de {contrib_login}...")
                    user_repos = fetch_user_repos(contrib_login)
                    
                    if contrib_id not in data["user_repositories"]:
                        data["user_repositories"][contrib_id] = {
                            "repos": [],
                            "repo_details": {}
                        }
                    
                    languages_used = defaultdict(lambda: {"count": 0, "total_stars": 0, "total_forks": 0})
                    
                    for urepo in user_repos:
                        urepo_id = str(urepo["id"])
                        
                        if urepo_id not in data["user_repositories"][contrib_id]["repos"]:
                            data["user_repositories"][contrib_id]["repos"].append(urepo["id"])
                        
                        data["user_repositories"][contrib_id]["repo_details"][urepo_id] = {
                            "github_id": urepo["id"],
                            "name": urepo["name"],
                            "full_name": urepo["full_name"],
                            "language": urepo.get("language"),
                            "stars": urepo.get("stargazers_count", 0),
                            "forks": urepo.get("forks_count", 0),
                            "description": urepo.get("description"),
                            "url": urepo.get("html_url")
                        }
                        
                        if urepo.get("language"):
                            lang = urepo["language"]
                            languages_used[lang]["count"] += 1
                            languages_used[lang]["total_stars"] += urepo.get("stargazers_count", 0)
                            languages_used[lang]["total_forks"] += urepo.get("forks_count", 0)
                            
                            if lang not in data["technologies"]:
                                data["technologies"][lang] = {
                                    "name": lang,
                                    "repositories_count": 0,
                                    "users_count": 0
                                }
                            if lang not in data["relationships"]["tech_to_users"]:
                                data["relationships"]["tech_to_users"][lang] = {"user_ids": []}
                            if int(contrib_id) not in [int(uid) for uid in data["relationships"]["tech_to_users"][lang]["user_ids"]]:
                                data["relationships"]["tech_to_users"][lang]["user_ids"].append(int(contrib_id))
                            data["technologies"][lang]["users_count"] = len(data["relationships"]["tech_to_users"][lang]["user_ids"])
                    
                    data["relationships"]["user_to_technologies"][contrib_id] = {
                        "languages": dict(languages_used)
                    }
                    
                    print(f"              ✅ {len(user_repos)} repositorios, {len(languages_used)} lenguajes")
                    
        except Exception as e:
            print(f"      ❌ Error obteniendo contribuidores: {e}")
    
    return data


def execute_query(query_config, verbose=False):
    name = query_config.get('name', 'Sin nombre')
    query = query_config.get('query', '')
    limit = query_config.get('limit', 5)
    
    if not query:
        print("⚠️  Query vacía, omitiendo...")
        return None
    
    print_header(f"🔍 {name}")
    print(f"   Query: {query}")
    print(f"   Límite: {limit} repositorios")
    
    data = {
        "metadata": {
            "query": query,
            "query_name": name,
            "fetched_at": datetime.now().isoformat(),
            "total_repos_fetched": 0,
            "total_users_found": 0
        },
        "repositories": {},
        "users": {},
        "technologies": {},
        "user_repositories": {},
        "relationships": {
            "repo_to_contributors": {},
            "user_to_owned_repos": {},
            "user_to_contributed_repos": {},
            "user_to_technologies": {},
            "tech_to_users": {},
            "tech_to_repos": {},
            "country_to_users": {}
        }
    }
    
    try:
        result = github_client.search_repositories(query=query, page=1)
        items = result.get('items', [])
        
        print(f"\n   ✅ Encontrados {len(items)} repositorios en GitHub")
        
        if items:
            repos_to_process = items[:limit]
            data["metadata"]["total_repos_fetched"] = len(repos_to_process)
            
            print(f"\n   📋 Procesando {len(repos_to_process)} repositorios...")
            
            for i, repo in enumerate(repos_to_process, 1):
                print(f"\n   [{i}/{len(repos_to_process)}]")
                data = process_repository(repo, query_config, data)
            
            data["metadata"]["total_users_found"] = len(data["users"])
            
            data["scores"] = calculate_scores(data)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = name.lower().replace(" ", "_").replace("/", "_")
            output_file = os.path.join(OUTPUT_DIR, f"{safe_name}_{timestamp}.json")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"\n   💾 Datos guardados en: {output_file}")
            print(f"   📊 Resumen:")
            print(f"      - Repositorios: {len(data['repositories'])}")
            print(f"      - Usuarios: {len(data['users'])}")
            print(f"      - Tecnologías: {len(data['technologies'])}")
            
            return data
            
    except Exception as e:
        print(f"\n   ❌ Error: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
    
    return None


def run_all_queries(config_path, verbose=False):
    print_header("🚀 EJECUTANDO TODAS LAS BÚSQUEDAS")
    print(f"   Archivo de configuración: {config_path}")
    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"\n   ❌ Archivo no encontrado: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"\n   ❌ Error JSON: {str(e)}")
        sys.exit(1)
    
    queries = config.get('queries', [])
    if not queries:
        print("\n   ⚠️  No hay consultas definidas")
        sys.exit(0)
    
    all_results = {
        "metadata": {
            "fetched_at": datetime.now().isoformat(),
            "total_queries": len(queries)
        },
        "results": []
    }
    
    for i, query_config in enumerate(queries, 1):
        print(f"\n\n[{i}/{len(queries)}]")
        try:
            result = execute_query(query_config, verbose)
            if result:
                all_results["results"].append({
                    "query_name": query_config.get('name'),
                    "query": query_config.get('query'),
                    "data": result
                })
        except Exception as e:
            print(f"\n   ❌ Error: {str(e)}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"all_queries_{timestamp}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print_separator()
    print(f"\n   💾 Resultados combinados guardados en: {output_file}")
    print(f"   📊 Total de búsquedas ejecutadas: {len(all_results['results'])}/{len(queries)}")
    print_separator()


def run_specific_query(config_path, name_filter, verbose=False):
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {config_path}")
        sys.exit(1)
    
    queries = config.get('queries', [])
    matching = [q for q in queries if name_filter.lower() in q.get('name', '').lower()]
    
    if not matching:
        print(f"⚠️  No se encontró '{name_filter}'")
        print("\n   Disponibles:")
        for q in queries:
            print(f"   - {q.get('name')}")
        sys.exit(0)
    
    for i, query_config in enumerate(matching, 1):
        print(f"\n[{i}/{len(matching)}]")
        execute_query(query_config, verbose)


def run_direct_query(query_string, limit, fetch_contributors, fetch_user_repos, verbose=False):
    query_config = {
        'name': 'Búsqueda Directa',
        'query': query_string,
        'limit': limit,
        'fetch_contributors': fetch_contributors,
        'fetch_user_repos': fetch_user_repos,
        'contributors_limit': 5
    }
    execute_query(query_config, verbose)


def list_queries(config_path):
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {config_path}")
        sys.exit(1)
    
    queries = config.get('queries', [])
    
    print_header("📋 BÚSQUEDAS DISPONIBLES")
    print(f"   Total: {len(queries)} búsquedas\n")
    
    for i, q in enumerate(queries, 1):
        print(f"   {i}. {q.get('name')}")
        print(f"      Query: {q.get('query')}")
        print(f"      Límite: {q.get('limit')} | Contrib: {'✓' if q.get('fetch_contributors') else '✗'}")
        print()
    
    print_separator()


def main():
    parser = argparse.ArgumentParser(
        description='Script de búsqueda en GitHub con exportación JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config/search_queries.json',
        help='Archivo de configuración JSON'
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Ejecutar todas las búsquedas'
    )
    
    parser.add_argument(
        '--name', '-n',
        help='Ejecutar búsqueda específica'
    )
    
    parser.add_argument(
        '--query', '-q',
        help='Query directa (ej: language:java stars:>50)'
    )
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=5,
        help='Número de repositorios (default: 5)'
    )
    
    parser.add_argument(
        '--contributors', '-C',
        action='store_true',
        help='Obtener contribuidores'
    )
    
    parser.add_argument(
        '--no-user-repos',
        action='store_true',
        help='No obtener repos de usuarios (más rápido)'
    )
    
    parser.add_argument(
        '--contributors-limit', '-cl',
        type=int,
        default=5,
        help='Límite de contribuidores por repo (default: 5)'
    )
    
    parser.add_argument(
        '--list', '-L',
        action='store_true',
        help='Listar búsquedas disponibles'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verbose'
    )
    
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Directorio de salida para JSON'
    )
    
    args = parser.parse_args()
    
    global OUTPUT_DIR
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), args.output_dir)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, args.config)
    
    if args.list:
        list_queries(config_path)
    elif args.all:
        run_all_queries(config_path, args.verbose)
    elif args.name:
        run_specific_query(config_path, args.name, args.verbose)
    elif args.query:
        run_direct_query(args.query, args.limit, args.contributors, not args.no_user_repos, args.verbose)
    else:
        parser.print_help()
        print("\n\n📌 Ejemplos:")
        print("   python scripts/test_search.py --all")
        print("   python scripts/test_search.py --name 'Java'")
        print("   python scripts/test_search.py -q 'language:python' -l 10 --contributors")


if __name__ == "__main__":
    main()
