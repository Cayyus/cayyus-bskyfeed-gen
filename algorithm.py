from atproto import Client, IdResolver, models
import os

import datetime
import pytz

import random
import bisect

class WeightedLottery:
    def __init__(self, term_data, seed=None):
        """Initialize with optional seed for deterministic behavior"""
        self.terms = term_data.copy()
        self.total_weight = 0
        self.cumulative_weights = []
        self.decayed_terms = []
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self._rebuild_cumulative_weights()
    
    def _rebuild_cumulative_weights(self):
        """Build the cumulative weight array that makes selection different"""
        self.cumulative_weights = []
        running_total = 0
        for term in self.terms:
            running_total += term['weight']
            self.cumulative_weights.append(running_total)
        
        self.total_weight = running_total
    
    def select_term(self):
        """Selects a term from the dictionary randomly"""
        if not self.terms or self.total_weight <= 0:
            return None
        
        random_value = random.uniform(0, self.total_weight)
        index = bisect.bisect_left(self.cumulative_weights, random_value)

        if index >= len(self.terms):
            index = len(self.terms) - 1
        return self.terms[index]

    def select_multiple_terms(self, count: int):
        """Select multiple terms without replacement"""
        if count <= 0:
            return []

        selected_terms = []
        available_terms = self.terms.copy()

        # Create temporary lottery for selection without replacement
        temp_lottery = WeightedLottery(available_terms, seed=self.seed)

        for _ in range(min(count, len(available_terms))):
            selected = temp_lottery.select_term()
            if selected:
                selected_terms.append(selected)
                available_terms = [t for t in available_terms if t['term'] != selected['term']]
                temp_lottery = WeightedLottery(available_terms, seed=None)  # No seed for subsequent selections

        self.adjust_weights(selected_terms)
        return selected_terms

    def adjust_weights(self, terms, decay_factor=0.3, recovery_factor=0.2):
        """Apply decay to selected terms and recovery to unselected terms"""
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
        
        # Cache for storing query batches with timestamps
        self.query_cache = {}
        self.cache_duration = 300  # 5 minutes in seconds
        
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
        
    def _generate_batch_id(self):
        """Generate a deterministic batch ID based on current time window"""
        # Create batches that last for 5 minutes
        time_window = int(time.time() // self.cache_duration)
        return f"batch_{time_window}"
    
    def _get_or_create_query_batch(self, batch_id):
        """Get existing query batch or create new one"""
        current_time = time.time()
        
        # Check if we have a cached batch that's still valid
        if batch_id in self.query_cache:
            batch_data = self.query_cache[batch_id]
            if current_time - batch_data['created_at'] < self.cache_duration:
                return batch_data['queries']
        
        # Generate new batch with deterministic seed
        seed = int(hashlib.md5(batch_id.encode()).hexdigest()[:8], 16)
        lottery = WeightedLottery(self.all_search_terms, seed=seed)
        selected_terms = lottery.select_multiple_terms(8)  # Generate more terms for variety
        queries = [term["term"] for term in selected_terms]
        
        # Cache the new batch
        self.query_cache[batch_id] = {
            'queries': queries,
            'created_at': current_time
        }
        
        # Clean old cache entries
        self._clean_old_cache_entries(current_time)
        
        return queries
    
    def _clean_old_cache_entries(self, current_time):
        """Remove expired cache entries"""
        expired_keys = [
            key for key, data in self.query_cache.items()
            if current_time - data['created_at'] > self.cache_duration * 2
        ]
        for key in expired_keys:
            del self.query_cache[key]

    def assign_weights(self):
        """Assign weights to terms based on category and specific adjustments"""
        category_weights = {
            'discipline_hashtags': 0.8,
            'languages_hashtags': 0.9,  # Fixed key name
            'tools': 0.7,
            'practices': 0.6,
            'specialty_hashtags': 1.2,
            'modern_hashtags': 1.0,
            'academic_hashtags': 1.1,
            'emerging': 1.3,
            'hardware': 1.4
        }
        
        term_adjustments = {
            '#Haskell': 1.5, '#Scala': 1.3, '#Rust': 1.2, '#Golang': 1.1,
            '#Python': 0.8, '#JavaScript': 0.8, '#Java': 0.9,
            '#biomedicalengineering': 1.3, '#aerospaceengineering': 1.3,
            '#chemicalengineering': 1.2,
            '#quantumcomputing': 1.4, '#RISCV': 1.4, '#WebAssembly': 1.3,
            '#edgecomputing': 1.2
        }
        
        for term_data in self.all_search_terms:
            term = term_data['term']
            category = term_data['category']
            
            weight = category_weights.get(category, 1.0)
            
            if term in term_adjustments:
                weight *= term_adjustments[term]
            
            # Add small random factor with fixed seed for consistency
            random.seed(hash(term) % 2**32)
            randomization_factor = random.uniform(0.9, 1.1)
            weight *= randomization_factor
            
            term_data['weight'] = weight
        
        # Normalize weights
        total_weight = sum(term['weight'] for term in self.all_search_terms)
        target_total = len(self.all_search_terms)
        
        normalization_factor = target_total / total_weight
        for term_data in self.all_search_terms:
            term_data['weight'] *= normalization_factor
        
        return self.all_search_terms

    def authenticate(self):
        """Authenticate with Bluesky"""
        self.client.login(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_PASSWORD"))

    def search_posts(self, q, limit=5):
        """Search for posts with given query"""
        try:
            search = self.client.app.bsky.feed.search_posts(params={"q": q, "limit": limit})
            return search.posts
        except Exception as e:
            print(f"Error searching for '{q}': {e}")
            return []

    def curate_feed(self):
        """Main method to curate the feed"""
        self.authenticate()
        
        # Parse cursor
        current_query_index = 0
        last_post_index = 0
        batch_id = self._generate_batch_id()

        if self.cursor:
            try:
                cursor_parts = self.cursor.split(":")
                if len(cursor_parts) >= 2:
                    current_query_index = int(cursor_parts[0])
                    last_post_index = int(cursor_parts[1])
                # If cursor has batch_id, use it to maintain consistency
                if len(cursor_parts) >= 3:
                    batch_id = cursor_parts[2]
            except (ValueError, IndexError):
                print(f"Invalid cursor format: {self.cursor}")
                pass

        # Get the query batch for this request
        queries = self._get_or_create_query_batch(batch_id)
        
        search_results = []
        next_cursor = None

        try:
            # Start from the current query index
            for i in range(current_query_index, len(queries)):
                query = queries[i]
                posts = self.search_posts(query, min(50, self.limit * 2))  # Get more posts to have options

                # Determine starting index for posts
                start_index = last_post_index if i == current_query_index else 0

                # Add posts from this query
                for j in range(start_index, len(posts)):
                    if len(search_results) >= self.limit:
                        # We have enough posts, set cursor for next request
                        next_cursor = f"{i}:{j}:{batch_id}"
                        break
                    
                    search_results.append(posts[j].uri)

                # If we have enough posts, break out of query loop
                if len(search_results) >= self.limit:
                    break

                # If we've finished this query and moving to next, reset post index
                if i < len(queries) - 1:
                    last_post_index = 0

            # If we've gone through all queries and still need more posts, generate next batch
            if len(search_results) < self.limit and current_query_index >= len(queries) - 1:
                # Move to next batch
                next_batch_id = f"batch_{int(time.time() // self.cache_duration) + 1}"
                next_cursor = f"0:0:{next_batch_id}"

        except Exception as e:
            print(f"Error in curate_feed: {e}")
            return {"error": str(e)}, 500

        # Prepare response
        feed_items = [{"post": uri} for uri in search_results[:self.limit]]
        response = {"feed": feed_items}

        if next_cursor and len(feed_items) == self.limit:
            response["cursor"] = next_cursor

        return response

    def publish_feed_generator(self):
        """Publish the feed generator to Bluesky"""
        self.authenticate()
        
        now = datetime.datetime.now(pytz.UTC)
        formatted_time = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_time = formatted_time[:-4] + "Z"

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
