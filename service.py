import json
from datetime import datetime, timedelta
from pymongo import MongoClient


GROUP_TYPES_FORMAT = {
    'hour':  '%Y-%m-%dT%H:00:00',
    'day':   '%Y-%m-%dT00:00:00',
    'month': '%Y-%m-01T00:00:00'
}


def validate_request_data(data):
    if not isinstance(data, dict):
        raise TypeError(f'Invalid data type: {type(data)} '
                        f'expected dict')
    if not all(key in data for key in ['dt_from', 'dt_upto', 'group_type']):
        raise ValueError('Missing required keys')
    group_type = data['group_type']
    if group_type not in GROUP_TYPES_FORMAT:
        raise ValueError(f'Invalid value of "group_type" key: {group_type}')


def execute_query(dt_from, dt_upto, time_unit):
    client = MongoClient('mongodb://127.0.0.1:27017/')
    db = client['sampleDB']
    collection = db['sample_collection']
    dt_format = GROUP_TYPES_FORMAT[time_unit]
    query = [
        {
            "$densify": {
                "field": "dt",
                "range": {
                    "step": 1,
                    "unit": time_unit,
                    "bounds": [dt_from, dt_upto + timedelta(days=1)]
                }
            }
        },
        {
            "$match": {"dt": {"$gte": dt_from, "$lte": dt_upto}}
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": dt_format, "date": "$dt"}},
                "totalValue": {"$sum": "$value"},
            },
        },
        {"$sort": {"_id": 1}},
    ]
    return collection.aggregate(query)


def get_aggregated_values(data):
    validate_request_data(data)
    dt_from = datetime.strptime(data['dt_from'], '%Y-%m-%dT%H:%M:%S')
    dt_upto = datetime.strptime(data['dt_upto'], '%Y-%m-%dT%H:%M:%S')
    group_type = data['group_type']
    result = execute_query(dt_from, dt_upto, group_type)
    labels, dataset = zip(*((it['_id'], it['totalValue']) for it in result))
    return json.dumps({'dataset': dataset, 'labels': labels})
