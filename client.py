"""Weighted Round Robin Balancer.
100% Python Standard Library.
"""
from typing import Dict, Any, List, Optional

class WeightedRoundRobinBalancer:
    """Nginx-style Smooth Weighted Round Robin (SWRR) Load Balancer."""
    def __init__(self):
        self.balancers: Dict[str, List[Dict[str, Any]]] = {}

    def add_target(self, balancer_id: str, target_name: str, weight: int = 1) -> Dict[str, Any]:
        if balancer_id not in self.balancers:
            self.balancers[balancer_id] = []

        targets = self.balancers[balancer_id]
        for t in targets:
            if t["name"] == target_name:
                t["weight"] = max(1, weight)
                return {"status": "updated", "target": target_name, "weight": t["weight"]}

        targets.append({
            "name": target_name,
            "weight": max(1, weight),
            "current_weight": 0,
            "healthy": True,
            "total_selected": 0
        })
        return {"status": "added", "target": target_name, "weight": weight}

    def select_next_target(self, balancer_id: str) -> Optional[Dict[str, Any]]:
        targets = [t for t in self.balancers.get(balancer_id, []) if t["healthy"]]
        if not targets:
            return None

        total_weight = sum(t["weight"] for t in targets)

        best = None
        for t in targets:
            t["current_weight"] += t["weight"]
            if best is None or t["current_weight"] > best["current_weight"]:
                best = t

        if best:
            best["current_weight"] -= total_weight
            best["total_selected"] += 1
            return {
                "selected_target": best["name"],
                "weight": best["weight"],
                "total_selected": best["total_selected"]
            }
        return None

    def set_target_health(self, balancer_id: str, target_name: str, healthy: bool = True) -> Dict[str, Any]:
        targets = self.balancers.get(balancer_id, [])
        for t in targets:
            if t["name"] == target_name:
                t["healthy"] = healthy
                return {"target": target_name, "healthy": healthy}
        return {"error": "Target not found"}

    def get_balancer_state(self, balancer_id: str) -> Dict[str, Any]:
        return {
            "balancer_id": balancer_id,
            "targets": self.balancers.get(balancer_id, [])
        }
