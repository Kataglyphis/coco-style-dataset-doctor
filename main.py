import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont
from pycocotools.coco import COCO
import os
import random
from tkinter import filedialog, messagebox, simpledialog

# Initialize customtkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class CocoDatasetGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("COCO Dataset GUI Tool")
        self.geometry("1000x700")

        # Initialize dataset variables
        self.coco = None
        self.image_folder = None
        self.image_ids = []
        self.current_index = 0

        # Class colors
        self.class_colors = {}
        self.classes = []

        # Setup GUI elements
        self.setup_gui()

        # Prompt user to select files
        self.select_files()

    def setup_gui(self):
        # Main frame
        self.frame = ctk.CTkFrame(master=self)
        self.frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Top frame for navigation and image info
        self.top_frame = ctk.CTkFrame(master=self.frame)
        self.top_frame.pack(pady=5, padx=5, fill="x")

        # Image index label
        self.image_index_label = ctk.CTkLabel(master=self.top_frame, text="Image 0/0")
        self.image_index_label.pack(side="left", padx=10)

        # Navigation buttons frame
        self.nav_frame = ctk.CTkFrame(master=self.top_frame)
        self.nav_frame.pack(side="right", padx=10)

        # Previous sample button
        self.prev_button = ctk.CTkButton(
            master=self.nav_frame, text="Previous Sample", command=self.prev_sample
        )
        self.prev_button.grid(row=0, column=0, padx=5)

        # Next sample button
        self.next_button = ctk.CTkButton(
            master=self.nav_frame, text="Next Sample", command=self.next_sample
        )
        self.next_button.grid(row=0, column=1, padx=5)

        # Image display label
        self.image_label = ctk.CTkLabel(master=self.frame, text="")
        self.image_label.pack(pady=10)

        # Bottom frame for class list and info
        self.bottom_frame = ctk.CTkFrame(master=self.frame)
        self.bottom_frame.pack(pady=5, padx=5, fill="x")

        # Classes textbox
        self.classes_textbox = ctk.CTkTextbox(master=self.bottom_frame, width=200)
        self.classes_textbox.pack(side="left", padx=10, pady=5)
        self.classes_textbox.configure(state="disabled")

        # Dataset info textbox
        self.info_textbox = ctk.CTkTextbox(master=self.bottom_frame, height=100)
        self.info_textbox.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        self.info_textbox.configure(state="disabled")

        # Control buttons frame
        self.control_frame = ctk.CTkFrame(master=self.frame)
        self.control_frame.pack(pady=10, padx=10, fill="x")

        # Button to change class ID of annotations
        self.change_class_button = ctk.CTkButton(
            master=self.control_frame,
            text="Change Class ID",
            command=self.change_class_id,
        )
        self.change_class_button.pack(side="left", padx=10)

        # Button to add another dataset
        self.add_dataset_button = ctk.CTkButton(
            master=self.control_frame,
            text="Add Another Dataset",
            command=self.add_dataset,
        )
        self.add_dataset_button.pack(side="left", padx=10)

        # Button to manage classes (change IDs or delete)
        self.manage_classes_button = ctk.CTkButton(
            master=self.control_frame,
            text="Manage Classes",
            command=self.manage_classes,
        )
        self.manage_classes_button.pack(side="left", padx=10)

    def select_files(self):
        # File dialog to select annotation file
        annotation_file = filedialog.askopenfilename(
            title="Select COCO Annotation File", filetypes=[("JSON Files", "*.json")]
        )
        if not annotation_file:
            messagebox.showerror("Error", "No annotation file selected.")
            self.quit()
            return

        # Directory dialog to select image folder
        image_folder = filedialog.askdirectory(title="Select COCO Image Folder")
        if not image_folder:
            messagebox.showerror("Error", "No image folder selected.")
            self.quit()
            return

        # Load COCO dataset
        try:
            self.coco = COCO(annotation_file)
            self.image_folder = image_folder
            self.image_ids = self.coco.getImgIds()
            self.current_index = 0

            # Get list of classes
            cats = self.coco.loadCats(self.coco.getCatIds())
            self.classes = [cat["name"] for cat in cats]
            self.assign_class_colors()

            # Update dataset information
            self.dataset_info = f"Total Images: {len(self.image_ids)}"
            self.update_info_textbox()
            self.update_classes_textbox()
            self.update_image_index_label()

            # Display the first image and annotations
            self.display_sample(self.current_index)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dataset: {e}")
            self.quit()

    def assign_class_colors(self):
        random.seed(42)  # For reproducibility
        for cat_id in self.coco.getCatIds():
            self.class_colors[cat_id] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )

    def update_info_textbox(self):
        self.info_textbox.configure(state="normal")
        self.info_textbox.delete("1.0", tk.END)
        self.info_textbox.insert("1.0", self.dataset_info)
        self.info_textbox.configure(state="disabled")

    def update_classes_textbox(self):
        self.classes_textbox.configure(state="normal")
        self.classes_textbox.delete("1.0", tk.END)
        self.classes_textbox.insert("1.0", "Classes:\n")
        for cat_id in self.coco.getCatIds():
            cat = self.coco.loadCats(cat_id)[0]
            self.classes_textbox.insert(tk.END, f"{cat_id}: {cat['name']}\n")
        self.classes_textbox.configure(state="disabled")

    def update_image_index_label(self):
        self.image_index_label.configure(
            text=f"Image {self.current_index + 1}/{len(self.image_ids)}"
        )

    def display_sample(self, index):
        if not self.image_ids:
            return

        # Get image info
        img_info = self.coco.loadImgs(self.image_ids[index])[0]
        image_path = os.path.join(self.image_folder, img_info["file_name"])

        # Open image
        try:
            image = Image.open(image_path).convert("RGB")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Image file not found: {image_path}")
            return

        # Draw annotations
        ann_ids = self.coco.getAnnIds(imgIds=img_info["id"])
        anns = self.coco.loadAnns(ann_ids)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        for ann in anns:
            bbox = ann["bbox"]
            x, y, w, h = bbox
            cat_id = ann["category_id"]
            color = self.class_colors.get(cat_id, (255, 0, 0))
            outline_color = tuple(color)
            draw.rectangle([x, y, x + w, y + h], outline=outline_color, width=2)

            # Get class id
            label = f"{cat_id}"

            # Calculate text size
            text_bbox = draw.textbbox((x, y), label, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # Draw label rectangle
            text_bg_rect = [x, y, x + text_width + 4, y + text_height + 4]
            draw.rectangle(text_bg_rect, fill=outline_color)

            # Draw text
            draw.text((x + 2, y + 2), label, fill="black", font=font)

        # Resize image to fit the GUI window
        image.thumbnail((800, 600))
        self.photo = ImageTk.PhotoImage(image)

        # Update image label
        self.image_label.configure(image=self.photo)
        self.image_label.image = self.photo

        # Update image index label
        self.update_image_index_label()

    def next_sample(self):
        if not self.image_ids:
            return
        # Increment index and loop back if necessary
        self.current_index = (self.current_index + 1) % len(self.image_ids)
        self.display_sample(self.current_index)

    def prev_sample(self):
        if not self.image_ids:
            return
        # Decrement index and loop back if necessary
        self.current_index = (self.current_index - 1) % len(self.image_ids)
        self.display_sample(self.current_index)

    def change_class_id(self):
        if not self.image_ids:
            return

        # Get current image annotations
        img_id = self.image_ids[self.current_index]
        ann_ids = self.coco.getAnnIds(imgIds=img_id)
        anns = self.coco.loadAnns(ann_ids)

        # Prompt user to select an annotation
        ann_options = [f"ID {ann['id']}: Cat {ann['category_id']}" for ann in anns]
        if not ann_options:
            messagebox.showinfo("Info", "No annotations to change.")
            return

        selected_ann = simpledialog.askstring(
            "Select Annotation",
            "Available Annotations:\n"
            + "\n".join(ann_options)
            + "\n\nEnter Annotation ID to change:",
        )
        if not selected_ann:
            return
        try:
            selected_ann_id = int(selected_ann)
        except ValueError:
            messagebox.showerror("Error", "Invalid annotation ID.")
            return

        # Check if the annotation ID exists
        ann = next((a for a in anns if a["id"] == selected_ann_id), None)
        if not ann:
            messagebox.showerror("Error", "Annotation ID not found.")
            return

        # Prompt for new class ID
        new_class_id = simpledialog.askinteger("New Class ID", "Enter new class ID:")
        if new_class_id is None:
            return

        # Change the class ID
        ann["category_id"] = new_class_id

        # Update the display
        self.display_sample(self.current_index)

    def add_dataset(self):
        # File dialog to select additional annotation file
        annotation_file = filedialog.askopenfilename(
            title="Select Additional COCO Annotation File",
            filetypes=[("JSON Files", "*.json")],
        )
        if not annotation_file:
            messagebox.showinfo("Info", "No annotation file selected.")
            return

        # Directory dialog to select image folder
        image_folder = filedialog.askdirectory(
            title="Select Additional COCO Image Folder"
        )
        if not image_folder:
            messagebox.showinfo("Info", "No image folder selected.")
            return

        # Load additional COCO dataset
        try:
            new_coco = COCO(annotation_file)
            new_image_folder = image_folder
            new_image_ids = new_coco.getImgIds()

            # Merge datasets
            self.merge_datasets(new_coco, new_image_folder)

            # Update dataset information
            self.dataset_info = f"Total Images: {len(self.image_ids)}"
            self.update_info_textbox()
            self.update_classes_textbox()
            self.update_image_index_label()

            # Display the current image
            self.display_sample(self.current_index)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load additional dataset: {e}")

    def merge_datasets(self, new_coco, new_image_folder):
        # Merge images
        new_images = new_coco.dataset["images"]
        self.coco.dataset["images"].extend(new_images)
        self.image_ids.extend(new_coco.getImgIds())

        # Merge annotations
        new_annotations = new_coco.dataset["annotations"]
        self.coco.dataset["annotations"].extend(new_annotations)

        # Merge categories
        new_cats = new_coco.dataset["categories"]
        existing_cat_ids = set(self.coco.getCatIds())
        for cat in new_cats:
            if cat["id"] not in existing_cat_ids:
                self.coco.dataset["categories"].append(cat)
                existing_cat_ids.add(cat["id"])

        # Rebuild index
        self.coco.createIndex()

        # Update class colors
        self.assign_class_colors()

        # Update class list
        cats = self.coco.loadCats(self.coco.getCatIds())
        self.classes = [cat["name"] for cat in cats]

    def manage_classes(self):
        # Open a new window
        self.manage_window = ctk.CTkToplevel(self)
        self.manage_window.title("Manage Classes")
        self.manage_window.geometry("400x600")

        # Create a scrollable frame if necessary
        canvas = tk.Canvas(self.manage_window)
        scrollbar = tk.Scrollbar(
            self.manage_window, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ctk.CTkFrame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # For each category, display current ID and name, entry for new ID, and delete checkbox
        self.class_entries = {}  # To store entries for new IDs
        self.class_delete_vars = {}  # To store variables for delete checkboxes
        row = 0
        for cat in self.coco.loadCats(self.coco.getCatIds()):
            cat_id = cat["id"]
            cat_name = cat["name"]

            # Display current ID and name
            label = ctk.CTkLabel(
                scrollable_frame, text=f"ID: {cat_id}, Name: {cat_name}"
            )
            label.grid(row=row, column=0, padx=5, pady=5, sticky="w")

            # Entry for new ID
            entry = ctk.CTkEntry(scrollable_frame)
            entry.grid(row=row, column=1, padx=5, pady=5)
            self.class_entries[cat_id] = entry

            # Checkbox for delete
            var = tk.BooleanVar()
            checkbox = ctk.CTkCheckBox(scrollable_frame, text="Delete", variable=var)
            checkbox.grid(row=row, column=2, padx=5, pady=5)
            self.class_delete_vars[cat_id] = var

            row += 1

        # Apply Changes button
        apply_button = ctk.CTkButton(
            scrollable_frame, text="Apply Changes", command=self.apply_class_changes
        )
        apply_button.grid(row=row, column=0, columnspan=3, pady=10)

    def apply_class_changes(self):
        # Collect new IDs and deletions
        new_ids = {}
        delete_ids = []
        existing_ids = set(self.coco.getCatIds())

        # First, collect new IDs and check for conflicts
        for cat_id, entry in self.class_entries.items():
            new_id_str = entry.get()
            if new_id_str:
                try:
                    new_id = int(new_id_str)
                    if new_id in existing_ids and new_id != cat_id:
                        messagebox.showerror(
                            "Error",
                            f"New ID {new_id} conflicts with existing category ID.",
                        )
                        return
                    new_ids[cat_id] = new_id
                except ValueError:
                    messagebox.showerror(
                        "Error", f"Invalid ID entered for category {cat_id}."
                    )
                    return

        # Collect categories to delete
        for cat_id, var in self.class_delete_vars.items():
            if var.get():
                delete_ids.append(cat_id)

        # Confirm deletion
        if delete_ids:
            result = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to delete categories {delete_ids}? This will remove all associated annotations.",
            )
            if not result:
                return

        # Apply changes
        # Update category IDs
        for old_id, new_id in new_ids.items():
            if old_id != new_id:
                # Update category ID in categories
                for cat in self.coco.dataset["categories"]:
                    if cat["id"] == old_id:
                        cat["id"] = new_id
                        break
                # Update category ID in annotations
                for ann in self.coco.dataset["annotations"]:
                    if ann["category_id"] == old_id:
                        ann["category_id"] = new_id
                # Update class colors
                if old_id in self.class_colors:
                    self.class_colors[new_id] = self.class_colors.pop(old_id)
                existing_ids.discard(old_id)
                existing_ids.add(new_id)

        # Delete categories and associated annotations
        if delete_ids:
            # Remove categories
            self.coco.dataset["categories"] = [
                cat
                for cat in self.coco.dataset["categories"]
                if cat["id"] not in delete_ids
            ]
            # Remove annotations
            self.coco.dataset["annotations"] = [
                ann
                for ann in self.coco.dataset["annotations"]
                if ann["category_id"] not in delete_ids
            ]
            # Remove class colors
            for del_id in delete_ids:
                if del_id in self.class_colors:
                    del self.class_colors[del_id]
            existing_ids = existing_ids.difference(set(delete_ids))

        # Rebuild the index
        self.coco.createIndex()

        # Update class colors
        self.assign_class_colors()

        # Update class list
        self.update_classes_textbox()

        # Refresh the display
        self.display_sample(self.current_index)

        # Close the manage window
        self.manage_window.destroy()

    # Additional methods can be added here


if __name__ == "__main__":
    app = CocoDatasetGUI()
    app.mainloop()