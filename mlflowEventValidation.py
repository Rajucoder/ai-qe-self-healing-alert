import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("self-healing-agent")

traces = mlflow.search_traces(max_results=1)

trace = traces.iloc[0]

print("Trace ID:", trace["trace_id"])

print("\nTrace column type:")
print(type(trace["trace"]))

print("\nTrace value:")
print(trace["trace"])

print("\nSpans column type:")
print(type(trace["spans"]))

print("\nSpans:")
print(trace["spans"])