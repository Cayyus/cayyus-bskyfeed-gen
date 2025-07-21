from atproto import Client, IdResolver, models
import os

import datetime
import pytz

import random
import bisect

class WeightedLottery:
    def __init__(self, term_data):
        self.terms = term_data.copy()
        self.total_weight = 0
        self.cumulative_weights = []
        self.decayed_terms = []
        self._rebuild_cumulative_weights()
    
    def _rebuild_cumulative_weights(self):
        """
        Build the cumulative weight array that makes selection different
        """
        running_total = 0
        for term in self.terms:
            running_total += term['weight']
            self.cumulative_weights.append(running_total)
        
        self.total_weight = running_total
    
    def select_term(self):
        """
        Selects a term from the dictionary randomly
        """
        if not self.terms or self.total_weight <= 0:
            return None
        
        random_value = random.uniform(0, self.total_weight)
        index = bisect.bisect_left(self.cumulative_weights, random_value)

        if index >= len(self.terms):
            index = len(self.terms) - 1
        return self.terms[index]

    def select_multiple_terms(self, count: int):
        if count <= 0:
            return []

        selected_terms = []
        available_terms = self.terms.copy()

        # Rebuild terms as you remove them
        temp_lottery = WeightedLottery(available_terms)

        for _ in range(min(count, len(available_terms))):
            selected = temp_lottery.select_term()
            if selected:
                selected_terms.append(selected)
                available_terms = [t for t in available_terms if t['term'] != selected['term']]
                temp_lottery =  WeightedLottery(available_terms)

        self.adjust_weights(selected_terms)
        return selected_terms

    def adjust_weights(self, terms, decay_factor=0.3, recovery_factor=0.2):
        """
        Applies a decay of decay_factor (%) to given terms eg. a decay factor of 0.3 means the terms become 30%
        of its original magnitude, or, applies a recovery factor to terms that were not given, eg 0.2 means weight is increased
        by 20%
        """
        term_names = {term['term'] for term in terms}

        for term_data in self.terms:
            if term_data['term'] in term_names:
                term_data['weight'] *= decay_factor
            else:
                term_data['weight'] *= (1 + recovery_factor)
        self._rebuild_cumulative_weights()

    def print_terms(self):
        print("Current terms and weights:")
        for term_data in self.terms:
            print(f"  Term: {term_data['term']:10} | Weight: {term_data['weight']:.4f}")
        print(f"  Total weight: {self.total_weight:.4f}\n")


class EngineerverseAlgorithm:
    def __init__(self, cursor, limit):
        self.client = Client()
        self.resolver = IdResolver()
        self.cursor = cursor
        self.limit = limit
        self.queries = None
        
        self.search_categories = {
            'discipline_hashtags': [
                "#engineering", "#programming", "#softwaredevelopment", "#computerscience"
            ],
            'specialty_hashtags': [
                "#mechanicalengineering", "#electricalengineering", "#civilengineering",
                "#chemicalengineering", "#biomedicalengineering", "#aerospaceengineering"
            ],
            'modern_hashtags': [
                "#datascience", "#machinelearning", "#artificialintelligence", "#cybersecurity",
                "#DevOps", "#IoT", "#robotics", "#automation"
            ],
            'academic_hashtags': [
                "#STEM", "#research", "#innovation", "#mathematics", "#physics"
            ],
            'languages_hashtags': [
                "#Python", "#JavaScript", "#Golang", "#Rust", "#Cpp", "#Java", "#CSharp",
                "#TypeScript", "#Swift", "#Kotlin", "#Ruby", "#PHP", "#Scala", "#Haskell"
            ],
            'tools': [
                "#ReactJS", "#Angular", "#VueJS", "#Django", "#Flask", "#SpringBoot",
                "#NodeJS", "#Docker", "#Kubernetes", "#AWS", "#Azure", "#TensorFlow", "#PyTorch"
            ],
            'practices': [
                "#agile", "#scrum", "#microservices", "#APIdevelopment", "#testing",
                "#debugging", "#optimization", "#architecture", "#designpatterns", "#codereview"
            ],
            'emerging': [
                "#blockchain", "#WebAssembly", "#GraphQL", "#serverless", "#quantumcomputing",
                "#edgecomputing", "#augmentedreality", "#virtualreality"
            ],
            'hardware': [
                "#Arduino", "#RaspberryPi", "#FPGA", "#PCB", "#embedded", "#RISCV"
            ]
        }
        
        # Flatten all search terms while maintaining their category information
        self.all_search_terms = []
        for category, terms in self.search_categories.items():
            for term in terms:
                self.all_search_terms.append({'term': term, 'category': category})
        self.assign_weights()
        self.lottery = WeightedLottery(self.all_search_terms)
        
    def assign_weights(self):
        """
        Assign weights to certain tags and words in descending order to ensure more popular topics have bigger
        presence but niche ones have considerable amounts too
        """
        # Strategy 1: Category-based weighting with inverse popularity
        # More popular categories get moderate weights, niche ones get boosted
        category_weights = {
            'discipline_hashtags': 0.8,    # Core CS/Engineering - high but not dominant
            'languages': 0.9,              # Programming languages - slightly higher
            'tools': 0.7,                  # Popular tools - moderate weight
            'practices': 0.6,              # Common practices - lower to allow niche content
            'specialty_hashtags': 1.2,     # Engineering specialties - boosted for diversity
            'modern_hashtags': 1.0,        # Trending topics - balanced weight
            'academic_hashtags': 1.1,      # Academic content - slightly boosted
            'emerging': 1.3,               # Cutting-edge tech - highest boost for discovery
            'hardware': 1.4                # Hardware topics - highest boost (most niche)
        }
        
        # Strategy 2: Term-specific adjustments within categories
        # Some terms within categories are more/less common than others
        term_adjustments = {
            # Boost less common but valuable languages
            '#Haskell': 1.5, '#Scala': 1.3, '#Rust': 1.2, '#Golang': 1.1,
            # Slightly reduce weight of very common languages
            '#Python': 0.8, '#JavaScript': 0.8, '#Java': 0.9,
            
            # Boost specialized engineering fields
            '#biomedicalengineering': 1.3, '#aerospaceengineering': 1.3,
            '#chemicalengineering': 1.2,
            
            # Boost emerging/niche technologies
            '#quantumcomputing': 1.4, '#RISC-V': 1.4, '#WebAssembly': 1.3,
            '#edge computing': 1.2
        }
        
        # Strategy 3: Apply weights with randomization for exploration
        
        for term_data in self.all_search_terms:
            term = term_data['term']
            category = term_data['category']
            
            # Start with category base weight
            weight = category_weights.get(category, 1.0)
            
            # Apply term-specific adjustments
            if term in term_adjustments:
                weight *= term_adjustments[term]
            
            # Add small random factor (±10%) for exploration
            # This prevents the algorithm from becoming too predictable
            randomization_factor = random.uniform(0.9, 1.1)
            weight *= randomization_factor
            
            # Store the final weight
            term_data['weight'] = weight
        
        # Strategy 4: Normalize weights to ensure they sum to reasonable total
        # This prevents any single category from dominating completely
        total_weight = sum(term['weight'] for term in self.all_search_terms)
        target_total = len(self.all_search_terms)  # Average weight of 1.0
        
        normalization_factor = target_total / total_weight
        for term_data in self.all_search_terms:
            term_data['weight'] *= normalization_factor
        
        return self.all_search_terms

    def authenticate(self):
        self.client.login(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_PASSWORD"))

    def publish_feed_generator(self):
        self.authenticate()
        
        # Create a properly formatted timestamp
        # Format: YYYY-MM-DDTHH:MM:SS.sssZ (note the 'Z' at the end indicating UTC)
        now = datetime.datetime.now(pytz.UTC)
        formatted_time = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        # Trim microseconds to 3 decimal places
        formatted_time = formatted_time[:-4] + "Z"

        # Create the feed generator record
        self.client.com.atproto.repo.create_record({
            "repo": self.client.me.did,
            "collection": "app.bsky.feed.generator",
            "rkey": "Engineerverse",
            "record": {
                "$type": "app.bsky.feed.generator",
                "did": "did:web:cayyus-bskyfeed-gen.onrender.com",
                "displayName": "Engineerverse by Cayyus",
                "description": "Includes engineering content, programming and software development and other science and math related stuff",
                "createdAt": formatted_time
            }
        })

    def search_posts(self, q, limit=5):
        search = self.client.app.bsky.feed.search_posts(params={"q": q, "limit": limit})
        return search.posts

    def curate_feed(self):
        self.authenticate()
        
        current_query_index = 0
        last_post_index = 0

        if self.cursor:
            try:
                cursor_parts = self.cursor.split(":")
                current_query_index = int(cursor_parts[0])
                last_post_index = int(cursor_parts[1])
            except (ValueError, IndexError):
                pass

        # Generate new queries if we don't have any OR if we've reached the end of current queries
        if not hasattr(self, 'queries') or not self.queries or current_query_index >= len(self.queries):
            selected_terms = self.lottery.select_multiple_terms(5)
            self.queries = [term["term"] for term in selected_terms]
            current_query_index = 0  # Reset to start of new query batch
            last_post_index = 0      # Reset post index for new batch

        search_results = []
        next_cursor = None

        try:
            for i in range(current_query_index, len(self.queries)):
                query = self.queries[i]
                posts = self.search_posts(query, 10)

                start_index = last_post_index if i == current_query_index else 0

                for j in range(start_index, len(posts)):
                    search_results.append(posts[j].uri)

                    if len(search_results) >= self.limit:
                        next_cursor = f"{i}:{j+1}"
                        break

                if len(search_results) >= self.limit:
                    break

                if i < len(self.queries) - 1:
                    next_cursor = f"{i+1}:0"

        except Exception as e:
            return 500, str(e)

        feed_items = [{"post": uri} for uri in search_results[:self.limit]]
        response = {"feed": feed_items}

        if next_cursor:
            response["cursor"] = next_cursor

        return response
