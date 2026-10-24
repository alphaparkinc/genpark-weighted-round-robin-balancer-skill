"""Example usage for GenPark Weighted Round Robin Balancer."""
from client import WeightedRoundRobinBalancer

def main():
    balancer = WeightedRoundRobinBalancer()
    cluster = "llm_gateway"

    balancer.add_target(cluster, "primary_claude_3_5", weight=3)
    balancer.add_target(cluster, "secondary_gpt_4o", weight=2)
    balancer.add_target(cluster, "fallback_deepseek", weight=1)

    print("Distributing 6 sequential requests via SWRR:")
    for i in range(6):
        selected = balancer.select_next_target(cluster)
        print(f" Request #{i+1} routed to: {selected['selected_target']}")

    print("
Cluster Balance State:")
    print(balancer.get_balancer_state(cluster))

if __name__ == "__main__":
    main()
