import re
import requests
from scrapy.selector import Selector
import urllib.parse
import time
import random


class WebContextFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def extract_entities(self, workflow):
        """Extract key entities from workflow description for context search"""
        entities = {
            'websites': [],
            'platforms': [],
            'tools': [],
            'domains': []
        }
        
        # Extract website URLs and domains
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        
        urls = re.findall(url_pattern, workflow, re.IGNORECASE)
        domains = re.findall(domain_pattern, workflow, re.IGNORECASE)
        
        entities['websites'].extend(urls)
        entities['domains'].extend([d for d in domains if not d.endswith('.com') or len(d.split('.')) > 1])
        
        # Extract common platforms and tools
        platform_keywords = [
            'facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'tiktok',
            'gmail', 'outlook', 'salesforce', 'hubspot', 'mailchimp', 'stripe',
            'shopify', 'wordpress', 'slack', 'discord', 'zoom', 'teams',
            'github', 'gitlab', 'jira', 'trello', 'asana', 'notion'
        ]
        
        tool_keywords = [
            'api', 'webhook', 'rss', 'csv', 'excel', 'database', 'sql',
            'automation', 'scraping', 'crawling', 'bot', 'script'
        ]
        
        workflow_lower = workflow.lower()
        
        for platform in platform_keywords:
            if platform in workflow_lower:
                entities['platforms'].append(platform)
        
        for tool in tool_keywords:
            if tool in workflow_lower:
                entities['tools'].append(tool)
        
        return entities
    
    def search_duckduckgo(self, query, max_results=5):
        """Search DuckDuckGo and return relevant snippets"""
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(0.5, 1.5))
            
            search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            selector = Selector(text=response.text)
            results = []
            
            # Find search result containers
            result_containers = selector.css("div.result")
            
            for container in result_containers[:max_results]:
                title = container.css("h2::text").get(default="").strip()
                snippet = container.css("div.result__snippet::text").get(default="").strip()
                
                if title and snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet
                    })
            
            return results
            
        except Exception as e:
            print(f"Search error for '{query}': {str(e)}")
            return []
    
    def fetch_live_context(self, workflow):
        """Fetch live context data for the workflow"""
        context = {
            'search_queries_performed': [],
            'findings': [],
            'api_availability': [],
            'blocking_reports': [],
            'alternatives_found': []
        }
        
        try:
            entities = self.extract_entities(workflow)
            
            # Build search queries based on extracted entities
            search_queries = []
            
            # Search for website/domain specific issues
            for domain in entities['domains'][:3]:  # Limit to avoid too many requests
                search_queries.append(f"{domain} API documentation")
                search_queries.append(f"{domain} scraping blocked captcha")
                search_queries.append(f"{domain} rate limiting access issues")
            
            # Search for platform specific automation
            for platform in entities['platforms'][:2]:
                search_queries.append(f"{platform} automation API webhook")
                search_queries.append(f"{platform} bot detection blocking")
            
            # Search for general automation context
            if entities['tools']:
                primary_tool = entities['tools'][0]
                search_queries.append(f"{primary_tool} automation best practices 2024")
            
            # Perform searches and analyze results
            for query in search_queries[:6]:  # Limit total searches
                context['search_queries_performed'].append(query)
                results = self.search_duckduckgo(query)
                
                for result in results:
                    self.analyze_search_result(result, context)
            
        except Exception as e:
            context['findings'].append(f"Live context fetch failed: {str(e)}")
        
        return context
    
    def analyze_search_result(self, result, context):
        """Analyze search result and categorize findings"""
        title = result['title'].lower()
        snippet = result['snippet'].lower()
        combined_text = f"{title} {snippet}"
        
        # Check for API availability indicators
        api_indicators = ['api', 'webhook', 'rss', 'feed', 'endpoint', 'documentation']
        if any(indicator in combined_text for indicator in api_indicators):
            if 'deprecated' not in combined_text and 'discontinued' not in combined_text:
                context['api_availability'].append(result['snippet'][:150])
        
        # Check for blocking/access issues
        blocking_indicators = [
            'blocked', 'banned', 'captcha', 'rate limit', 'anti-bot',
            'detection', 'cloudflare', 'access denied', 'forbidden'
        ]
        if any(indicator in combined_text for indicator in blocking_indicators):
            context['blocking_reports'].append(result['snippet'][:150])
        
        # Check for alternatives
        alternative_indicators = [
            'alternative', 'instead', 'better way', 'workaround',
            'official method', 'recommended approach'
        ]
        if any(indicator in combined_text for indicator in alternative_indicators):
            context['alternatives_found'].append(result['snippet'][:150])
        
        # General relevant findings
        relevance_indicators = [
            'automation', 'integrate', 'connect', 'export', 'import',
            'sync', 'schedule', 'trigger', 'workflow'
        ]
        if any(indicator in combined_text for indicator in relevance_indicators):
            if len(context['findings']) < 10:  # Limit findings
                context['findings'].append(result['snippet'][:150])
    
    def format_context_for_gemini(self, context):
        """Format context data into a concise summary for Gemini"""
        summary = []
        
        if context['api_availability']:
            summary.append("API/Feed Options Found:")
            for api_info in context['api_availability'][:3]:
                summary.append(f"• {api_info}")
        
        if context['blocking_reports']:
            summary.append("Access/Blocking Issues Reported:")
            for blocking_info in context['blocking_reports'][:3]:
                summary.append(f"• {blocking_info}")
        
        if context['alternatives_found']:
            summary.append("Alternative Approaches Found:")
            for alt_info in context['alternatives_found'][:2]:
                summary.append(f"• {alt_info}")
        
        if context['findings']:
            summary.append("General Automation Context:")
            for finding in context['findings'][:3]:
                summary.append(f"• {finding}")
        
        if not summary:
            summary.append("No specific live context found for this workflow.")
        
        return '\n'.join(summary)