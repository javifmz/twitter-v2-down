
import argparse, yaml, json
from pathlib import Path
from searchtweets import load_credentials, gen_request_parameters, ResultStream, collect_results

endpoint_search = 'https://api.twitter.com/2/tweets/search/all'
endpoint_count = 'https://api.twitter.com/2/tweets/counts/all'

# Argument parser
parser = argparse.ArgumentParser(description='Download tweets using the Twitter API V2')
parser.add_argument('--config', type=str, help='configuration file (by defaul "config.yml")', default='config.yml')
parser.add_argument('--output', type=str, help='output directory file (by defaul "output")', default='output')
args = parser.parse_args()

# Load configuration
with open(args.config) as config_file :
  config = yaml.load(config_file, Loader=yaml.FullLoader)

# Load credentials
credentials = config['credentials']
bearer_token = credentials['bearer_token']

# Load data
data = config['data']
expansions = data['expansions'] if 'expansions' in data else ''
tweet_fields = data['tweet_fields'] if 'tweet_fields' in data else ''
user_fields = data['user_fields'] if 'user_fields' in data else ''
place_fields = data['place_fields'] if 'place_fields' in data else ''

# Load entities
entities = config['entities']
entities_index = 1
for entity_id, entity in entities.items() :
  
  query = entity['query']
  date_from = entity['date_from']
  date_to = entity['date_to']
  print(f'Entity "{entity_id}" ({entities_index}/{len(entities)}): query "{query}" from {date_from} to {date_to}')

  count_rule = gen_request_parameters(query, results_per_call=100, granularity="day", start_time=date_from, end_time=date_to)
  counts = collect_results(count_rule, result_stream_args={ 'endpoint': endpoint_count, 'bearer_token': bearer_token })
  count = sum(item['tweet_count'] for c in counts for item in c['data'])
  print(f'- {entity_id}: {count} tweets in total')

  query_rs = gen_request_parameters(query, results_per_call=100, granularity=None, start_time=date_from, end_time=date_to, expansions=expansions, tweet_fields=tweet_fields, user_fields=user_fields, place_fields=place_fields)
  rs = ResultStream(request_parameters=query_rs, max_tweets=10000000, max_results=10000000, endpoint=endpoint_search, bearer_token=bearer_token)
  path = Path(f'{args.output}/{entity_id}')
  path.mkdir(parents=True, exist_ok=True)      
  index = 0
  for data in rs.stream() :
    index += 1
    with open(f'{args.output}/{entity_id}/{index:07d}.json', 'w') as f :
      json.dump(data, f)
      print(f'- {entity_id}: Page {index} downloaded')
  print(f'- {entity_id}: Done!')

  entities_index += 1