## 9. Architecture Diagram Code

### `architecture_diagram.py`
python
"""
Generate architecture diagram for the Reddit Streaming Pipeline
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines

# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(14, 10))

# Define colors
color_source = '#FF4500'  # Reddit orange
color_kafka = '#231F20'   # Kafka black
color_spark = '#E25A1C'   # Spark orange
color_mongo = '#4DB33D'   # MongoDB green
color_dashboard = '#FF6B6B'  # Dashboard red
color_docker = '#2496ED'  # Docker blue

# Component boxes
components = [
    {'name': 'Reddit API\n(PRAW)', 'pos': (1, 7), 'color': color_source},
    {'name': 'Producer\n(Python)', 'pos': (3, 7), 'color': '#3776AB'},
    {'name': 'Apache Kafka\n(Message Broker)', 'pos': (5, 7), 'color': color_kafka},
    {'name': 'Spark Streaming\n(Consumer)', 'pos': (7, 7), 'color': color_spark},
    {'name': 'MongoDB\n(Storage)', 'pos': (9, 7), 'color': color_mongo},
    {'name': 'Streamlit\n(Dashboard)', 'pos': (11, 7), 'color': color_dashboard},
    {'name': 'Zookeeper\n(Coordination)', 'pos': (5, 5), 'color': '#6B8E23'},
]

# Draw components
for comp in components:
    box = FancyBboxPatch(
        (comp['pos'][0]-0.4, comp['pos'][1]-0.3),
        0.8, 0.6,
        boxstyle="round,pad=0.1",
        facecolor=comp['color'],
        edgecolor='black',
        alpha=0.7,
        linewidth=2
    )
    ax.add_patch(box)
    ax.text(comp['pos'][0], comp['pos'][1], comp['name'], 
            ha='center', va='center', fontsize=9, 
            color='white', weight='bold')

# Draw Docker container
docker_box = FancyBboxPatch(
    (0.2, 4.2), 11.6, 4.2,
    boxstyle="round,pad=0.1",
    facecolor=color_docker,
    edgecolor=color_docker,
    alpha=0.1,
    linewidth=3,
    linestyle='--'
)
ax.add_patch(docker_box)
ax.text(6, 4.5, 'Docker Compose Environment', 
        ha='center', va='center', fontsize=11, 
        color=color_docker, weight='bold', style='italic')

# Draw arrows
arrows = [
    ((1.4, 7), (2.6, 7), 'Stream'),
    ((3.4, 7), (4.6, 7), 'Publish'),
    ((5.4, 7), (6.6, 7), 'Consume'),
    ((7.4, 7), (8.6, 7), 'Process'),
    ((9.4, 7), (10.6, 7), 'Query'),
    ((5, 6.7), (5, 5.3), 'Coordinate'),
]

for start, end, label in arrows:
    arrow = FancyArrowPatch(
        start, end,
        arrowstyle='->,head_width=0.4,head_length=0.8',
        color='black',
        linewidth=2,
        connectionstyle="arc3,rad=0"
    )
    ax.add_patch(arrow)
    # Add label
    mid_x = (start[0] + end[0]) / 2
    mid_y = (start[1] + end[1]) / 2 + 0.2
    ax.text(mid_x, mid_y, label, ha='center', va='bottom', fontsize=8)

# Add ports and URLs
ax.text(11, 6.5, 'http://localhost:8501', ha='center', fontsize=8, style='italic')
ax.text(9, 6.5, 'mongodb://localhost:27017', ha='center', fontsize=8, style='italic')
ax.text(5, 6.5, 'localhost:9092', ha='center', fontsize=8, style='italic')

# Add title
ax.text(6, 8.5, 'Reddit Real-Time Streaming Pipeline Architecture', 
        ha='center', va='center', fontsize=14, weight='bold')

# Add data flow indicators
ax.text(1, 8, 'Data Source', ha='center', fontsize=9, color='gray')
ax.text(6, 8, 'Stream Processing', ha='center', fontsize=9, color='gray')
ax.text(11, 8, 'Visualization', ha='center', fontsize=9, color='gray')

# Set axis properties
ax.set_xlim(0, 12)
ax.set_ylim(4, 9)
ax.axis('off')

# Save the diagram
plt.tight_layout()
plt.savefig('architecture_diagram.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()

print("Architecture diagram saved as 'architecture_diagram.png'")