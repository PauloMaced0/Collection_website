$( document ).ready(function() {
    const path = window.location.href;

    function makeImageCard(image) {
        let ret = '<div class="card container" style="width: 18rem;">';
        ret += `<img src="${image.img_path}" class="card-img-top" alt="...">`;
        ret += '<div class="card-body">';
        let text = image.name;
        const str = text.split(".")[0]
        ret += `<h5 class="card-title">${str}</h5>`;
        ret += `<a href="/labiproj6/image?id=${image.id_image}" class="btn btn-primary">Mais info</a>`;
        if (image.owner == null) {
            ret += `<button class="btn btn-success" type="button" value="${image.id_image}">Adquirir</button>`
        }
        ret += '</div></div>';
                    
        return ret;
    }

    const params = path.split("?")[1];
    const id = params.split("=")[1];

    $.get(
        `/labiproj6/cromos?id=${id}`,
        function(data) {
            console.log(data);
            let to_append = "";
            for (const image of data) {
                to_append += makeImageCard(image);
            }

            $( "#div_content").append(to_append);
        }
    )

    $( "#div_content" ).on("click", "button", function(event) {
        const image_id = event.currentTarget.value;
        $.ajax({
            type: "POST",
            url: "/labiproj6/cromos/draft",
            data: {
                "id": image_id,
            },
            success: function(data) {
                console.log(data);
                alert("Cromo adquirido!");
                location.reload();
            },
            error: function() {
                alert("Ocurreu um erro. Tente novamente.");
            }
        });
    });
});

