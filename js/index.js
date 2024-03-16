const droparea = document.querySelector(".drag-file");

        droparea.addEventListener("dragover", (e) => {
            e.preventDefault();
            droparea.classList.add("hover");
        });

        droparea.addEventListener("dragleave", () => {
            droparea.classList.remove("hover");
        });

        droparea.addEventListener("drop", (e) => {
            e.preventDefault();

            const image = e.dataTransfer.files[0];
            const type = image.type;

            if (type == "image/png" || type == "image/jpg" || type == "image/jpeg") {
                upload(image);
                console.log(image);
            } else {
                droparea.setAttribute("class", "drag-file invalid");
                droparea.innerText = "Invalid File Format!!!";
            }
        });

        const upload = (image) => {
            const formData = new FormData();
            formData.append("file", image);

            fetch("/upload", {
                method: "POST",
                body: formData
            })
                .then(response => response.text())
                .then(result => {
                    console.log(result);
                    displayUploadedFile(image.name);
                })
                .catch(error => {
                    console.error('Error:', error);
                });

            droparea.setAttribute("class", "drag-file valid");
            droparea.innerText = "Added " + image.name;



            // 파일을 선택한 경우 변수에 저장
            selectedFile = image;
        };

        const displayUploadedFile = (filename) => {
            const filesDiv = document.getElementById("files");
            const fileDiv = document.createElement("div");
//            fileDiv.classList.add("file");

            // fileDiv.innerHTML = `
            //     <div class="thumbnail">
            //         <img src="${filepath}" alt="Uploaded Image" class="image">
            //     </div>
            //     <div class="details">
            //         <header class="header">
            //             <span class="name">${filename}</span>
            //             <span class="size">7.5 mb</span>
            //         </header>
            //         <div class="progress">
            //             <div class="bar"></div>
            //         </div>
            //         <div class="status">
            //             <span class="percent">100% done</span>
            //             <span class="speed">90KB/sec</span>
            //         </div>
            //     </div>
            // `;

//            filesDiv.appendChild(fileDiv);
        };

        const uploadFile = () => {
            const fileInput = document.getElementById("chooseFile");
            const file = fileInput.files[0];

            if (file) {
                upload(file);
            }
        };

         const submitAndConfirm = () => {
            const filename = selectedFile.name;

            // 서버로 파일 업로드 요청 보내기
            upload(selectedFile);

            // 사용자에게 확인 메시지 표시
            const confirmationMessage = `제출 성공! 업로드한 이미지(${filename})를 확인합니다.`;
            alert(confirmationMessage);



            //window.location.href = "{{ url_for('display_uploaded_file', filename='') }}/" + filename;
            // Flask 스타일의 URL 동적 생성
            const url = `/uploads/${filename}`;
//            const url = `/uploads`;

            const countDownDuration = 5000;

            function Redirect() {
                window.location.href = url;
            }

            setTimeout(Redirect, countDownDuration);


        };