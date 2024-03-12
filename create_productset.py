from google.cloud import vision
import os
from time import sleep
from threading import Thread



"""
This is the driver code to create the product set by using the product set functionality in Google Cloud Vision 
and link the set to the images uploaded to the GCP bucket through the uploaded CSV bulk import files.
Since any error will result in the entire process stopping, try-except is applied so that minor errors
(usually 1 import error) will not terminate the whole bulk product set import procedure.
"""

start = 0
end = 40

def main():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:\\Users\\user\\Downloads\\markit_key.json"
    for num in range(start, end):
        try:
            func(num)
            num += 1
            print(f'processed file no. image_output_{num}')
            # sleep(900)  # Sleep for 900 seconds (15 minutes)
            print("Operation complete:", num)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Operation complete:", num)
            continue

def remove_product_from_product_set(project_id, location, product_id, product_set_id):
        """Remove a product from a product set.
        Args:
            project_id: Id of the project.
            location: A compute region name.
            product_id: Id of the product.
            product_set_id: Id of the product set.
        """
        client = vision.ProductSearchClient()

        # Get the full path of the product set.
        product_set_path = client.product_set_path(
            project=project_id, location=location, product_set=product_set_id
        )

        # Get the full path of the product.
        product_path = client.product_path(
            project=project_id, location=location, product=product_id
        )

        # Remove the product from the product set.
        client.remove_product_from_product_set(name=product_set_path, product=product_path)
        client.list_product_sets()
        print("Product removed from product set.")
        client.list_product_sets('projects/markit-live-v2/')


def create_product_set(project_id, location, product_set_id, product_set_display_name):
    """Create a product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
        product_set_display_name: Display name of the product set.
    """
    client = vision.ProductSearchClient()

    # A resource that represents Google Cloud Platform location.
    location_path = f"projects/{project_id}/locations/{location}"

    # Create a product set with the product set specification in the region.
    product_set = vision.ProductSet(display_name=product_set_display_name)

    # The response is the product set with `name` populated.
    response = client.create_product_set(
        parent=location_path, product_set=product_set, product_set_id=product_set_id
    )

    # Display the product set information.
    print(f"Product set name: {response.name}")


def import_product_sets(project_id, location, gcs_uri):
    """Import images of different products in the product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        gcs_uri: Google Cloud Storage URI.
            Target files must be in Product Search CSV format.
    """
    client = vision.ProductSearchClient()

    # A resource that represents Google Cloud Platform location.
    location_path = f"projects/{project_id}/locations/{location}"

    # Set the input configuration along with Google Cloud Storage URI
    gcs_source = vision.ImportProductSetsGcsSource(csv_file_uri=gcs_uri)
    input_config = vision.ImportProductSetsInputConfig(gcs_source=gcs_source)

    # Import the product sets from the input URI.
    response = client.import_product_sets(
        parent=location_path, input_config=input_config
    )

    print(f"Processing operation name: {response.operation.name}")
    # synchronous check of operation status
    result = response.result()
    print("Processing done.")

    for i, status in enumerate(result.statuses):
        print("Status of processing line {} of the csv: {}".format(i, status))
        # Check the status of reference image
        # `0` is the code for OK in google.rpc.Code.
        if status.code == 0:
            reference_image = result.reference_images[i]
            print(reference_image)
        else:
            print(f"Status code not OK: {status.message}")


def func(numv):
    docnum = numv
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:\\Users\\user\\Downloads\\markit_key.json"
    # create_product_set('app', 'asia-northeast03', 'example-set', 'vision-example-set') example one liner
    csv_uri = f"gs://markit23-v2/image_output_{docnum}.csv"
    import_product_sets('markit-live-v2', 'us-west1', csv_uri)
    print("the imported one is:", csv_uri)


if __name__ == '__main__':
    main()
