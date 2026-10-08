from flask import Blueprint, request, jsonify
from collector.log_parser import parse_raw_input, extract_summary
from api.ai_integration import analyze_compliance
from database.db import (
    save_scan,
    save_compliance_items,
    get_all_scans,
    get_scan_by_id,
    get_latest_scan,
    get_compliance_items,
    get_compliance_summary,
    clear_all_scans
)

api = Blueprint("api", __name__)


@api.route("/api/submit", methods=["POST"])
def submit():
    data = request.get_json()
    if not data or not data.get("raw_output"):
        return jsonify({"error": "No output provided."}), 400
    raw_output = data["raw_output"].strip()
    if len(raw_output) < 20:
        return jsonify({"error": "Output too short."}), 400

    sections  = parse_raw_input(raw_output)
    summary   = extract_summary(sections)
    ai_result = analyze_compliance(sections, summary)

    clear_all_scans()
    scan_id = save_scan(
        raw_output = raw_output,
        ai_summary = ai_result["summary"],
        ai_raw     = ai_result["raw"]
    )
    save_compliance_items(scan_id, ai_result["items"])

    return jsonify({
        "scan_id": scan_id,
        "summary": ai_result["summary"],
        "items":   ai_result["items"],
        "specs":   summary
    }), 200


@api.route("/api/latest", methods=["GET"])
def latest():
    scan = get_latest_scan()
    if not scan:
        return jsonify({"message": "No scans yet."}), 204
    items  = get_compliance_items(scan["id"])
    counts = get_compliance_summary(scan["id"])
    return jsonify({"scan": scan, "items": items, "counts": counts}), 200


@api.route("/api/history", methods=["GET"])
def history():
    scans = get_all_scans()
    return jsonify({"scans": scans}), 200


@api.route("/api/scan/<int:scan_id>", methods=["GET"])
def scan_detail(scan_id):
    scan = get_scan_by_id(scan_id)
    if not scan:
        return jsonify({"error": "Scan not found."}), 404
    items  = get_compliance_items(scan_id)
    counts = get_compliance_summary(scan_id)
    return jsonify({"scan": scan, "items": items, "counts": counts}), 200


@api.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "online"}), 200