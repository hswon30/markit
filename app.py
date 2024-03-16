from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
import re
from google.cloud import vision
import math
app = Flask(__name__)
import base64
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from PIL import Image, ImageOps
import time

#GLOBALS
##################################################################################################################
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# global variables
URL = "https://storage.googleapis.com/markit23-v2"
product_set_id = "vision-live"
product_category = "general-v1"
project_id = "markit-live-v2"
location = "us-west1"
max_results = 3
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:\\Users\\Yejin\\Documents\\gcloud_api.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:\\Users\\user\\Downloads\\markit_key.json"
# for session cookie
app.secret_key = "hswon_my_secret_key"          # -> 이게 뭘 의미하는지 모르겠음22222222
#############################################################################################################


# vertex ai
################################################################################################################
vin_dict = {
    "Circles":"원형",
    "Lines,bands,bars":"선,봉",
    "Squares":"정사각형",
    "Rectangles":"직사각형",
    "Natural_phenomena":"자연현상",
    "Cats,dogs,wolves,foxes,bears,lions,tigers":"육식동물",
    "Birds,bats":"조류,박쥐",
    "Parts_of_the_human_body,skeletons,skulls":"인체",
    "Polygons(geometric_figures_with_five_or_more_sides)":"폴리곤",
    "Trees,bushes":"나무,수풀",
    "Inscriptions":"각인",
    "Diamonds":"마름모",
    "Men":"사람",
    "Shields,crests":"방패,인장",
    "Headwear":"모자",
    "Stars,comets":"별,혜성",
    "Globes": "지구",
    "Sun":"태양",
    "Leaves,branches_with_leaves_or_needles,needles":"나뭇잎",
    "Ovals":"타원"
}

#vertex AI 모델 사용
def predict_image_object_detection_sample(
    project: str,
    endpoint_id: str,
    filename: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com"
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    with open(filename, "rb") as f:
        file_content = f.read()

    # The format of each instance should conform to the deployed model's prediction input schema.
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    instance = predict.instance.ImageObjectDetectionPredictionInstance(
        content=encoded_content,
    ).to_value()
    instances = [instance]
    # See gs://google-cloud-aiplatform/schema/predict/params/image_object_detection_1.0.0.yaml for the format of the parameters.
    parameters = predict.params.ImageObjectDetectionPredictionParams(
        confidence_threshold=0.0,
        max_predictions=10,
    ).to_value()
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)
    # See gs://google-cloud-aiplatform/schema/predict/prediction/image_object_detection_1.0.0.yaml for the format of the predictions.
    predictions = response.predictions
    print(predictions)
    for prediction in predictions:
        print(" prediction:", dict(prediction))
        res = dict(prediction)['displayNames']
        final = []
        for item in res:
            if item in vin_dict.keys():
                final.append(vin_dict[item])
                print(vin_dict[item])
        final = set(final)
        print("final list is:", list(final))
        final = list(final)[-3:]
        print(final)

        return final

###################################################################################################################3
#제품검색
def product_search(
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


    #FIXME
    with open(file_path, "rb") as image_file:
        content = image_file.read()
        # content = res_img.read()

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

    # 결과 코드(실제 실행시에는 comment out)
    print("Search results:")
    for result in results:
        product = result.product

        print(f"Score(Confidence): {result.score}")
        print(f"Image name: {result.image}")

        print(f"Product name: {product.name}")
        print("Product display name: {}".format(product.display_name))
        print(f"Product description: {product.description}\n")
        print(f"Product labels: {product.product_labels}\n")
    return results

# 인터넷에 노출된 img패스 찾는 코드. 직접 for문 돌려서 3번 실행 or 코드 수정
def find_path(whole_path):
    print("Find-path is called")

    # Define a regex pattern to match the desired part
    pattern = r"/([^/]+)$"

    # Use re.search to find the match
    match = re.search(pattern, whole_path)

    # Check if a match is found
    if match:
        # Extract the matched part
        res = match.group(1)
        # year = res.split("_")[0]

        print("The full path is:", f'{URL}/{res}.jpg')
        return f'{URL}/{res}.jpg'

    else:
        print("No match found.")



@app.route('/')
def index():
    session.modified = True
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        #resize
        file.save(filename)


        img = Image.open(file)
        res_img = img.resize((1024, 1024))
        res_img = ImageOps.exif_transpose(res_img)

        res_img.save(filename)

        # # Create a BytesIO object
        # output_buffer = BytesIO()
        #
        # # Save the resized image to the BytesIO object
        # res_img.save(output_buffer, format='JPEG')  # Adjust the format as needed
        #
        # # Get the contents of the BytesIO object
        # content = output_buffer.getvalue()

        print("file is saved normally")
        # img = Image.open(filename)
        #
        # fin_img = img.resize((512, 512))
        # print("filename is:", filename)
        #
        # fin_img.save(filename)

        # driver code for final results
        results = product_search(project_id, location, product_set_id,
                                 product_category, filename, "", max_results)


        # driver code for vertex results
        vertex_res = predict_image_object_detection_sample(
            project="markit-live-v2",
            endpoint_id="7456898854693109760",
            location="us-central1",
            filename=filename
        )



        session['vertex_res'] = vertex_res
        session.modified = True

        serializable_results = [
            {
                'score': round(res.score, 2),
                'image': res.image,
                'product_name': res.product.name,
            }
            for res in results
        ]

        print("sending results:", serializable_results)

        session['image_results'] = serializable_results
        session.modified = True


        return redirect(url_for('display_uploaded_file', filename=file.filename))
        #return filename  # Return the uploaded file's path



#@app.route('/uploads/<filename>')
# @app.route('/uploads')
@app.route('/uploads/<filename>')
def display_uploaded_file(filename):
    print("Filename in display_uploaded_file:", filename)
    results = session['image_results']
    vertex_res = session['vertex_res']
    return render_template('result.html', results=results, filename=filename, find_path=find_path, ceil = math.ceil, vertex_res = vertex_res)


# js 경로 찾기
@app.route('/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.abspath(os.path.dirname(__file__))
    return send_from_directory(os.path.join(root_dir, 'static'), filename)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
    #serve(app, host='127.0.0.1', port=8000)
