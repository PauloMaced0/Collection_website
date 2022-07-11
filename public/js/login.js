$( document).ready(function() {
    function setCookie(cname, cvalue, exdays) {
        const d = new Date();
        d.setTime(d.getTime() + (exdays*24*60*60*1000));
        const expires = "expires=" + d.toUTCString();
        const max_age = ";max-age=" + d.toUTCString();
        const samesite = ";SameSite=Lax";
        document.cookie = cname + "=" + cvalue + ";" + expires + max_age + samesite + ";path=/";
    }
    $( "#button_login" ).click(function() {
        const username = $( "#input_username" ).val();
        const password = $( "#input_password" ).val();

        $.ajax({
            type: "POST",
            url: "/labiproj6/users/auth",
            data: {
                "username": username,
                "password": password,
            },
            success: function(data) {
                setCookie("username", username, 10);
                setCookie("token", data.token, 10);
                window.location.replace("/labiproj6/");
            },
            error: function(request) {
                if (request.status === 404) {
                    alert("Nome de utilizador e palavra-passe não coincidem. Tente novamente.")
                }
            }
            
        });
    });
});
