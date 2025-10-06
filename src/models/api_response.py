# utils.py
from typing import Tuple

from flask import jsonify, Response


class APIResponse:
    @staticmethod
    def response(message: str) -> tuple[Response, int]:
        return jsonify({"message": message}), 200

    @staticmethod
    def bad_request(message: str) -> tuple[Response, int]:
        return jsonify({"message": message}), 400

    @staticmethod
    def forbidden(message: str = "Access denied") -> tuple[Response, int]:
        return jsonify({"message": message}), 403

    @staticmethod
    def not_found(message: str) -> tuple[Response, int]:
        return jsonify({"message": message}), 404

    @staticmethod
    def conflict(message: str) -> tuple[Response, int]:
        return jsonify({"message": message}), 409

    @staticmethod
    def internal_error(message: str = "Internal server error") -> tuple[Response, int]:
        return jsonify({"message": message}), 500
