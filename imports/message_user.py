import matplotlib.pyplot as plt

def show_message_plot(message, instructions):
    """
    Display a plot with a specified message and instructions.

    Parameters:
    - message (str): The message to display.
    - instructions (str): The instructions to display.
    """
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Hide the axes
    ax.axis('off')

    # Add the message and instructions to the plot
    ax.text(0.5, 0.6, message, fontsize=24, fontweight='bold', ha='center', va='center')
    ax.text(0.5, 0.4, instructions, fontsize=14, ha='center', va='center')

    # Display the plot
    plt.show(block=True)