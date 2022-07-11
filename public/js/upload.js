$( document ).ready(function() {

    function upload(collection_name, file) {
        const formData = new FormData();

        formData.append("name", collection_name);
        formData.append("file", file);

        $.ajax({
            type: "POST",
            url: "/labiproj6/cromos/name/create",
            success: function (data) {
                console.log(data);
            },
            error: function (error) {
                console.log(error);
            },
            async: true,
            data: formData,
            cache: false,
            contentType: false,
            processData: false,
            timeout: 60000
        });
    }

    $( "#btn_form_submit" ).click(function() {
        const collection_name = $( "#input_collection_name").val();
        const input_images = document.getElementById("input_images");

        // var fileExtension = ['jpeg', 'jpg'];
        // if ($.inArray($(this).val().split('.').pop().toLowerCase(), fileExtension) == -1) {
        //     alert("Formatos válidos: "+fileExtension.join(', '));
        // }

        if (collection_name == null || collection_name == "") {
            alert("Nome da coleção não introduzido. Tente novamente.");
            return;
        }

        if (input_images.files.length === 0) {
            alert("Imagens não introduzidas. Tente novamente.");
            return;
        }

        for (const file of input_images.files) {
            upload(collection_name, file);
        }

        input_images.value = null;
    })
});