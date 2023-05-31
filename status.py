
import argparse, yaml, json, os, re
from pathlib import Path
from collections import Counter
from searchtweets import load_credentials, gen_request_parameters, ResultStream, collect_results

endpoint_count = 'https://api.twitter.com/2/tweets/counts/all'

# Argument parser
parser = argparse.ArgumentParser(description='Download tweets using the Twitter API V2')
parser.add_argument('--config', type=str, help='configuration file (by defaul "config.yml")', default='config.yml')
parser.add_argument('--output', type=str, help='output directory file (by defaul "output")', default='output')
args = parser.parse_args()

# Load configuration
with open(f'/app/{args.config}') as config_file :
  config = yaml.load(config_file, Loader=yaml.FullLoader)

# Load credentials
credentials = config['credentials']
bearer_token = credentials['bearer_token']

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
  total = sum(item['tweet_count'] for c in counts for item in c['data'])
  print(f'+ {entity_id}: {total} tweets in total')

  counts1 = [ (re.sub(r'T.*$', '', item['start']), item['tweet_count']) for c in counts for item in c['data'] ]
  counts1.sort(key=lambda x: x[0])

  count = 0
  counts2 = Counter()
  path = Path(f'{args.output}/{entity_id}')
  for entity_file in os.listdir(f'{args.output}/{entity_id}') :
    with open(f'{args.output}/{entity_id}/{entity_file}') as file :
      content = json.load(file)
      data = content['data']
      for tweet in data :
        date = tweet['created_at']
        date = re.sub(r'T.*$', '', date)
        counts2.update({ date: 1 })
      count += len(data)

  real_sum, expected_sum = 0, 0
  for date, expected in counts1 :
    real = counts2[date]
    real_sum += real
    expected_sum += expected
    print(f'  - {date}: {real}/{expected} tweets ({real/expected*100}%)')

  print(f'+ {entity_id}: {real_sum}/{expected_sum} tweets {real_sum/expected_sum*100}%')
  
  entities_index += 1