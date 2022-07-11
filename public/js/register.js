$(document).ready(function() {
    $( "#button_register" ).click(function() {
        const username = $( "#input_username" ).val();
        const password = $( "#input_password" ).val();
        const password_confirm = $( "#input_password_confirm" ).val();

        if (username.length < 4) {
            alert("Nome de utilizador deve ter pelo menos 4 caracteres.");
            return;
        }

        if (password.length < 8) {
            alert("Palavra-passe deve conter pelo menos 8 caracteres")
            return;
        }

        if (password !== password_confirm) {
            alert("Palavra-passe não coincide. Tente novamente.")
            return;
        }

        $.ajax({
            type: "POST",
            url: "/labiproj6/users/create",
            data: {
                "username": username,
                "password": password,
            },
            success: function() {
                window.location.replace("/labiproj6/login");
            },
            error: function(request) {
                if (request.status === 409) {
                    alert("Nome de utilizador em uso. Tente novamente.");
                }
            }
        });
    });
});
