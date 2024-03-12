from google.cloud import vision
import os
"""
# Output CSV file
output_csv = "image_output_1.csv"

# Default values
def_product_set_id = "example-set"
def_product_category = "general-v1"

"""



"""
This is a separate exercise to fetch matching products from the product set created with Google cloud vision.
The first function is a helper function to return the full GCP bucket address of the matched product image links
and the second function is the driver function for getting matching products from the existing product set.
"""

URL = "the correct path to the open url"

def find_path(whole_path):
    import re


    # Define a regex pattern to match the desired part
    pattern = r"products/(\d+_\d+)/"

    # Use re.search to find the match
    match = re.search(pattern, whole_path)

    # Check if a match is found
    if match:
        # Extract the matched part
        res = match.group(1)
        year = res.split("_")[0]
        filename = res.split("_")[1]

        print(res)
        return URL + year + filename
    else:
        print("No match found.")



def get_similar_products_file(
    project_id,
    location,
    product_set_id,
    product_category,
    file_path,
    filter,
    max_results,
):
    """Search similar products to image.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
        product_category: Category of the product.
        file_path: Local file path of the image to be searched.
        filter: Condition to be applied on the labels.
                Example for filter: (color = red OR color = blue) AND styles = kids
                It will search on all products with the following labels:
                color:red AND styles:kids
                color:blue AND styles:kids
        max_results: The maximum number of results (matches) to return. If omitted, all results are returned.
    """
    # product_search_client is needed only for its helper methods.
    product_search_client = vision.ProductSearchClient()
    image_annotator_client = vision.ImageAnnotatorClient()

    # Read the image as a stream of bytes.
    with open(file_path, "rb") as image_file:
        content = image_file.read()

    # Create annotate image request along with product search feature.
    image = vision.Image(content=content)

    # product search specific parameters
    product_set_path = product_search_client.product_set_path(
        project=project_id, location=location, product_set=product_set_id
    )
    product_search_params = vision.ProductSearchParams(
        product_set=product_set_path,
        product_categories=[product_category],
        filter=filter,
    )
    image_context = vision.ImageContext(product_search_params=product_search_params)

    # Search products similar to the image.
    response = image_annotator_client.product_search(
        image, image_context=image_context, max_results=max_results
    )

    index_time = response.product_search_results.index_time
    print("Product set index time: ")
    print(index_time)

    results = response.product_search_results.results

    print("Search results:")
    for result in results:
        product = result.product

        print(f"Score(Confidence): {result.score}")
        print(f"Image name: {result.image}")

        print(f"Product name: {product.name}")
        print("Product display name: {}".format(product.display_name))
        print(f"Product description: {product.description}\n")
        print(f"Product labels: {product.product_labels}\n")

def main():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:\\Users\\user\\Downloads\\gcloud_key.json"
    """
    # Output CSV file
    output_csv = "image_output_1.csv"

    # Default values
    def_product_set_id = "example-set"
    def_product_category = "general-v1"
    def_region = 'us-west1'
    :return:
    """

    product_set_id = "example-set"
    product_category = "general-v1"
    project_id = "appteam01"
    #location of the
    location = "us-west1"
    file_path = "./beats.png"
    max_results = 5

    get_similar_products_file(project_id=project_id, product_set_id=product_set_id, location=location, filter="",
                              product_category=product_category, file_path=file_path, max_results=max_results)

if __name__ == '__main__':
    main()