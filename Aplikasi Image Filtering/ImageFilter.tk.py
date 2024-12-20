from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

# Global variable for file path
filename = ""
original_image = None
filtered_image = None

# Helper Functions
def browse_files():
    """Browse image files from the device."""
    global filename, original_image
    filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select an Image",
        filetypes=(("Image files", ".jpg *.jpeg *.png"), ("All files", ".*"))
    )
    if filename:
        label_file_explorer.config(text=f"Selected File: {filename}")
        try:
            original_image = cv2.imread(filename)
            display_image(original_image, canvas_before)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
    else:
        messagebox.showwarning("Warning", "No file selected!")

def save_file():
    """Save the filtered image to the device."""
    global filtered_image
    if filtered_image is not None:
        try:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=(("PNG files", ".png"), ("JPEG files", ".jpg .jpeg"), ("All files", ".*"))
            )
            if save_path:
                # Convert image from BGR to RGB before saving
                image_rgb = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(image_rgb)
                img_pil.save(save_path)
                messagebox.showinfo("Success", "Image saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")
    else:
        messagebox.showwarning("Warning", "No filtered image to save!")

def display_image(image, canvas):
    """Display the given image on the specified canvas."""
    try:
        # Convert image to RGB (for PIL compatibility)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(image_rgb)

        # Resize image to fit canvas (416x416)
        img_resized = img_pil.resize((416, 416), Image.Resampling.LANCZOS)

        # Create Tkinter-compatible image
        tk_img = ImageTk.PhotoImage(img_resized)
        canvas.delete("all")  # Clear the canvas
        canvas.image = tk_img
        canvas.create_image(0, 0, anchor=NW, image=tk_img)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to display image: {e}")

def apply_filter(filter_func):
    """Apply the selected filter to the image."""
    global original_image, filtered_image
    if original_image is not None:
        try:
            filtered_image = filter_func(original_image)
            display_image(filtered_image, canvas_after)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filter: {e}")
    else:
        messagebox.showwarning("Warning", "No image selected!")

# Filter Functions
def prewitt(img):
    """Prewitt edge detection filter."""
    # Convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Prewitt Kernel
    kernel_x = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])
    kernel_y = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
    
    # Compute Prewitt gradient
    grad_x = cv2.filter2D(gray, -1, kernel_x)
    grad_y = cv2.filter2D(gray, -1, kernel_y)
    
    # Combine gradients
    prewitt_grad = cv2.addWeighted(grad_x, 0.5, grad_y, 0.5, 0)
    return cv2.cvtColor(prewitt_grad, cv2.COLOR_GRAY2BGR)  # Return back to BGR format for display

def sketch(img):
    """Sketch filter using edge detection."""
    # Convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Invert the grayscale image
    inverted_gray = cv2.bitwise_not(gray)

    # Apply Gaussian blur to the inverted image
    blurred = cv2.GaussianBlur(inverted_gray, (21, 21), sigmaX=0, sigmaY=0)

    # Invert the blurred image
    inverted_blurred = cv2.bitwise_not(blurred)

    # Combine original gray image with inverted blurred image to create a sketch effect
    sketch_image = cv2.divide(gray, inverted_blurred, scale=256.0)

    # Return image in BGR format for compatibility with the GUI
    return cv2.cvtColor(sketch_image, cv2.COLOR_GRAY2BGR)

# Main GUI Creation
def create_gui():
    """Create the main graphical user interface."""
    window = Tk()
    window.title("Image Filter Application")
    window.configure(bg="#2E2E2E")

    # Title Frame
    create_title_frame(window)

    # File Explorer Frame
    create_file_explorer_frame(window)

    # Canvas for Before and After Images
    create_canvas_frame(window)

    # Filter Buttons Frame
    create_filter_buttons_frame(window)

    # Save Button
    create_save_button_frame(window)

    # Footer
    create_footer(window)

    # Run Main Loop
    window.mainloop()

def create_title_frame(window):
    """Creates the title section of the GUI."""
    title_frame = Frame(window, bg="#2E2E2E")
    title_frame.pack(pady=15)
    Label(
        title_frame, 
        text="Image Filter Application", 
        font=("Helvetica", 28, "bold"), 
        bg="#2E2E2E", 
        fg="#D3D3D3"
    ).pack()

def create_file_explorer_frame(window):
    """Creates the file explorer section of the GUI."""
    file_frame = Frame(window, bg="#2E2E2E")
    file_frame.pack(pady=15)
    global label_file_explorer
    label_file_explorer = Label(
        file_frame, 
        text="No File Selected", 
        bg="#3A3A3A", 
        fg="#D3D3D3", 
        width=60, 
        anchor="w", 
        relief="sunken", 
        padx=10, 
        font=("Arial", 10)
    )
    label_file_explorer.pack(side=LEFT, padx=10)
    Button(
        file_frame, 
        text="Browse", 
        command=browse_files, 
        bg="#32CD32", 
        fg="#FFFFFF", 
        padx=15, 
        pady=5, 
        font=("Arial", 10, "bold"), 
        relief="flat", 
        highlightthickness=0, 
        bd=0, 
        overrelief="groove", 
        highlightbackground="#32CD32",
        borderwidth=0
    ).pack(side=LEFT)

def create_canvas_frame(window):
    """Creates the canvas section for displaying before and after images."""
    canvas_frame = Frame(window, bg="#2E2E2E")
    canvas_frame.pack(pady=15, padx=15)

    global canvas_before, canvas_after
    Label(canvas_frame, text="Original", bg="#2E2E2E", fg="#D3D3D3", font=("Arial", 12)).grid(row=0, column=0, padx=10)
    Label(canvas_frame, text="Filtering", bg="#2E2E2E", fg="#D3D3D3", font=("Arial", 12)).grid(row=0, column=1, padx=10)

    canvas_before = Canvas(canvas_frame, width=416, height=416, bg="#3A3A3A", highlightthickness=0)
    canvas_before.grid(row=1, column=0, padx=10)

    canvas_after = Canvas(canvas_frame, width=416, height=416, bg="#3A3A3A", highlightthickness=0)
    canvas_after.grid(row=1, column=1, padx=10)

def create_filter_buttons_frame(window):
    """Creates the filter buttons frame."""
    filter_frame = Frame(window, bg="#2E2E2E")
    filter_frame.pack(pady=20)
    filter_buttons = [
        ("Prewitt", prewitt),  # Prewitt filter
        ("Sketch", sketch),    # Sketch filter
    ]
    for text, func in filter_buttons:
        Button(
            filter_frame, 
            text=text, 
            command=lambda f=func: apply_filter(f), 
            bg="#0000FF", 
            fg="#FFFFFF", 
            padx=15, 
            pady=5, 
            font=("Arial", 10, "bold"), 
            relief="flat", 
            highlightthickness=0, 
            bd=0, 
            overrelief="groove", 
            highlightbackground="#0000FF",
            borderwidth=0
        ).pack(side=LEFT, padx=10)

def create_save_button_frame(window):
    """Creates the save button section."""
    save_frame = Frame(window, bg="#2E2E2E")
    save_frame.pack(pady=10)
    Button(
        save_frame, 
        text="Save Image", 
        command=save_file, 
        bg="#FF4500", 
        fg="#FFFFFF", 
        padx=15, 
        pady=5, 
        font=("Arial", 10, "bold"), 
        relief="flat", 
        highlightthickness=0, 
        bd=0, 
        overrelief="groove", 
        highlightbackground="#FF4500",
        borderwidth=0
    ).pack(side=LEFT)

def create_footer(window):
    """Creates the footer section."""
    footer_frame = Frame(window, bg="#2E2E2E")
    footer_frame.pack(pady=5)
    Label(
        footer_frame, 
        text="© 2024 Tugas Pengolahan Citra", 
        bg="#2E2E2E", 
        fg="#A9A9A9", 
        font=("Arial", 8)
    ).pack()

# Run Application
if __name__ == "__main__":
    create_gui()
