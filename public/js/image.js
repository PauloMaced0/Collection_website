$(document).ready(function () {
    function makeImageCard(image) {
        let ret = '<div class="p-3 mb-2 bg-light text-dark text-center w-75" style="margin-left:14%">';
        ret += '<h2>Informações</h2>';
        ret += `Proprietário: ${image.owner} <br>`;
        const creation_date = new Date(image.creation_date);
        ret += `Data de criação: ${creation_date.toLocaleString()} <br>`;
        ret += `Criada por: ${image.uploaded_by} <br>`;
        ret += `Nome da sua coleção: ${image.collection_name} <br>`;
        let text = image.img_name;
        const str = text.split(".")[0]
        ret += `Nome da imagem: ${str} <br>`;
        ret += '<h6 class="text-center container" style="margin-top: 2%;">Transações:</h6>'
        for (const data of image.transactions) {
            const tranf_date = new Date(data.ts);
            ret += `Data: ${tranf_date.toLocaleString()} <br>`
            ret += `Proprietário: ${data.owner} <br>`
        }
        
        ret += '</div>';    

        return ret;
    }

    const path = window.location.href;
    const params = path.split("?")[1];
    const id = params.split("=")[1];

    $.get(
        `/labiproj6/cromos/image?id=${id}`,
        function (data) {
            if (data.able_to_transfer === false) {
                $("#transfer_div").remove();
            }

            const to_append = makeImageCard(data);
            $("#div_content").append(to_append);

        }
    );

    $( "#btn_transfer" ).click(function() {
        const new_owner = $( "#input_new_owner" ).val();

        if (new_owner == null || new_owner === "") {
            alert("Nome de utilizador não especificado. Tente novamente");
            return;
        }

        $.post(
            "/labiproj6/cromos/transfer",
            {
                "id": id,
                "new_owner": new_owner
            }
        ).done(function() {
            alert("Imagem transferida");
            location.reload();
        }).fail(function(data) {
            if(data.status === 404) {
                alert("Utilizador não encontrado. Tente novamente");
            }
            console.log(data);
        });
    });
});
