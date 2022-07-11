$(document).ready(function () {
    function makeCollectionCard(collection) {

        let ret = '<div class="card container" style="width: 18rem;">';
        ret += `<img src="${collection.img_path}" class="card-img-top" alt="">`;
        ret += '<div class="card-body">';
        ret += `<h5 class="card-title">${collection.name}</h5>`;
        ret += `<a href="/labiproj6/collection?id=${collection.id_collection}" class="btn btn-primary">Ver</a>`;
        ret += '</div></div>';

        return ret;
    }
    $.get(
        "/labiproj6/cromos/",
        function (data) {
            let to_append = "";
            for (const collection of data) {
                to_append += makeCollectionCard(collection);
            }

            $("#div_content").append(to_append);
        }
    )

});
