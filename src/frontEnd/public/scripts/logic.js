function logout(){

        let cliente = JSON.parse(localStorage.getItem("cliente"));

        cliente = {
            id: null,
            nome: "",
            isAdmin: false,
        };

        localStorage.setItem("cliente", JSON.stringify(cliente));

        window.location.href = "homePage.html"; 
}