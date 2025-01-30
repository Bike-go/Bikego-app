from flask import Blueprint, jsonify, request
from datetime import datetime
from models.statistics_model import Statistics
from schemas.statistics_schema import StatisticsSchema

statistics_bp = Blueprint("statistics_bp", __name__)

# GET route to retrieve the latest statistics
@statistics_bp.route("/statistics/latest", methods=["GET"])
def get_latest_statistics():
    latest_statistics = Statistics.query.order_by(Statistics.report_period.desc()).first()
    if not latest_statistics:
        return jsonify({"msg": "No statistics available"}), 404
    return StatisticsSchema().jsonify(latest_statistics), 200

# GET route to retrieve statistics for a specific period
@statistics_bp.route("/statistics", methods=["GET"])
def get_statistics_by_period():
    start_period = request.args.get("start")
    end_period = request.args.get("end")

    if not start_period or not end_period:
        return jsonify({"msg": "Start and end period parameters are required"}), 400

    try:
        start_date = datetime.fromisoformat(start_period)
        end_date = datetime.fromisoformat(end_period)
    except ValueError:
        return jsonify({"msg": "Invalid date format. Use ISO format (YYYY-MM-DD)"}), 400

    statistics = Statistics.query.filter(
        Statistics.report_period.between(start_date, end_date)
    ).all()

    if not statistics:
        return jsonify({"msg": "No statistics available for this period"}), 404
    return StatisticsSchema(many=True).jsonify(statistics), 200