import matplotlib.pyplot as plt

# Processing times in seconds
times = [
    1.2224, 0.9986, 0.9058, 1.0802, 1.1157, 1.0802,
    1.0575, 1.1277, 1.1194, 1.0832, 1.0258, 1.1180
]

# Compute average
avg_time = sum(times) / len(times)
print(f"Average processing time: {avg_time:.4f} seconds")

# Plot the values
plt.figure(figsize=(10, 5))
plt.plot(times, marker='o')
plt.xlabel("Run #")
plt.ylabel("Time (seconds)")
plt.title("Processing Pipeline Time per Run")
plt.grid(True)

# Save plot as PDF
plt.savefig("pipeline_times.pdf", bbox_inches="tight")

plt.show()
