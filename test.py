import heapq

def min_moves(n, m, passengers):
    graph = {i: [] for i in range(n)}

    for s, f in passengers:
        graph[s].append((f, 1))
        graph[f].append((s, 1))

    def dijkstra(start):
        distances = {i: float('inf') for i in range(n)}
        distances[start] = 0
        heap = [(0, start)]

        while heap:
            current_distance, current_vertex = heapq.heappop(heap)

            if current_distance > distances[current_vertex]:
                continue

            for neighbor, weight in graph[current_vertex]:
                distance = current_distance + weight

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(heap, (distance, neighbor))

        return distances  # بازگشت فاصله‌ها

    total_moves = 0
    for i in range(m):
        distances = dijkstra(passengers[i][0])
        total_moves += distances[passengers[i][1]]

    return total_moves

# خواندن ورودی
n, m = map(int, input().split())
passengers = [tuple(map(int, input().split())) for _ in range(m)]

# محاسبه و چاپ خروجی
result = min_moves(n, m, passengers)
print(result)
