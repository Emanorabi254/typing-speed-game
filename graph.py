from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

def embed_score_graph(parent, scores):
    if not scores:
        return
    fig = plt.figure(figsize=(5, 2.5), dpi=100)
    plt.plot(range(1, len(scores)+1), scores, marker='o', color="#FCD150")
    plt.title("Score Over Time")
    plt.xlabel("Attempt #")
    plt.ylabel("Score")
    plt.grid(True)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
