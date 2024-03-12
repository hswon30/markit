import os
import csv


"""
This is a simple python exercise to create CSV files for bulk import of products and linked images
into a Google Cloud Vision product set. CSV file is a requirement for bulk import, which is far more efficient
than iterating over each of the files in the Cloud bucket to include them in a product set.
Since we are only using one product set, the code is initialized for all CSV files to have the same product set name.
Furthermore, since each instance of bulk import can take in 20,000 lines, 
each CSV file is limited to listing 19,999 products each.
"""


#directory containing your images
image_directory = "C:\\Users\\user\\Downloads\\gcp_images"
print("image directory set up")

num = 1
# Output CSV file
output_csv = f'image_output_{num}.csv'

# Default values
def_product_set_id = "vision-live"
def_product_category = "general-v1"


DEFAULT_URI = "gs://markit23-v2/"


#function to decode a text file for google cloud uris

# Function to write a line to the CSV file
#FIXME this needs to write to a new file every 20,000 images
def write_csv_line(csv_writer, image_uri, image_id, product_set_id, product_id, product_category, product_display_name=" ", labels="", bounding_poly=""):
    csv_writer.writerow([image_uri, image_id, product_set_id, product_id, product_category, product_display_name, labels, bounding_poly])



# Open CSV file for writing
with open(output_csv, mode='w', newline='') as csv_file:
    initial = 0
    csv_writer = csv.writer(csv_file)

    # Write header to the CSV file
    csv_writer.writerow(["image-uri", "image-id", "product-set-id", "product-id", "product-category",
                         "product-display-name", "labels", "bounding-poly"])

    # Iterate through images in the directory
    for filename in os.listdir(image_directory):
        if filename.endswith(".jpg"):
            initial += 1
            image_path = os.path.join(image_directory, filename)
            gs_product_id = os.path.splitext(filename)[0]  # Use filename as product_id
            gs_image_uri = DEFAULT_URI + filename
            gs_image_id = ""

            # Write a line to the CSV file
            write_csv_line(csv_writer, image_uri=gs_image_uri, image_id=gs_image_id,
                           product_set_id=def_product_set_id, product_id=gs_product_id,
                           product_category=def_product_category)
            if initial == 19997:
                print(f"CSV file '{output_csv}' generated successfully.")
                csv_file.close()
                num += 1
                output_csv = f'image_output_{num}.csv'
                csv_file = open(output_csv, mode='w', newline='')
                csv_writer = csv.writer(csv_file)
                initial = 0
                csv_writer.writerow(["image-uri", "image-id", "product-set-id", "product-id", "product-category",
                                     "product-display-name", "labels", "bounding-poly"])


print(f"CSV file '{output_csv}' generated successfully.")
