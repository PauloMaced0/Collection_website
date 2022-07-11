$(document).ready(function () {
    function make_user_password(info) {
        let ret = `<p class="fs-4"> Nome do utilizador: ${info.username}</p>`;
        return ret;
    }

    function make_user_collection(info) {
        let ret = '<div class="card container" style="width: 18rem;">';
        ret += `<img src="${info.img_path}" class="card-img-top" alt="...">`;
        ret += '<div class="card-body">';
        let text = info.img_name;
        const str = text.split(".")[0]
        ret += `<h6 class="card-title ">${str}</h6>`;
        ret += '</div></div>'
        return ret;
    }

    $.get(
        "/labiproj6/users/profile",
        function (data) {
            console.log(data);
            let images_owned = "";
            let username_password = "";
            if (data.length !== 0){
                username_password += make_user_password(data[0]);
            }
            
            for (const info of data) {
                images_owned += make_user_collection(info);
            }

            $("#div_content_profile").append(username_password)
            $("#div_content").append(images_owned)
        }
    )
})