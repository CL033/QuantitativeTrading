import datetime
from collections import OrderedDict

from flask import Flask, Blueprint, request, jsonify
import json, time
from query.query import SQL_Query
from model.tongyi_online import create_model

common = Blueprint('common', __name__, url_prefix='/common')


def custom_json_dumps(obj):
    if isinstance(obj, OrderedDict):
        return {k: v for k, v in obj.items()}
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


@common.route('/query', methods=['POST'])
def query():
    query_msg = request.form.get('searchMsg')
    # data = query.get_json()
    # 检查数据是否有效
    if query_msg is None:
        return jsonify({"error": "'query' parameter is missing"}), 400
    model = create_model()
    sql_query = SQL_Query(model)
    result = sql_query.query(query_msg)
    print('查询结果', result)
    print(type(result))
    ordered_json = json.dumps(result, default=custom_json_dumps, indent=4).encode("utf-8")
    return ordered_json
