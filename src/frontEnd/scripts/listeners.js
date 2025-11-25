// listener para alterar o nome no canto superior direito
document.addEventListener("DOMContentLoaded", () => {

        const cliente = JSON.parse(localStorage.getItem("cliente"));

                if (cliente && cliente.nome) {
                const botaoLogin = document.getElementById("loginName");
                botaoLogin.textContent = cliente.nome;

                botaoLogin.onclick = () => mostrarSecao('sec-perfil');
        }

});
//admin@admin.com leagueoflegendsehlegal

//listener para definir botoes que o user normal nao pode ver
document.addEventListener("DOMContentLoaded", () => {
        const cliente = JSON.parse(localStorage.getItem("cliente"));
        console.log("Cliente:", cliente);

        const btnCadastro = document.getElementById("btnCadastrarEspaco");
        
        if (!cliente.isAdmin) {
                btnCadastro.style.display = "none";
        }

});

document.addEventListener("DOMContentLoaded", () => {
    let cliente = JSON.parse(localStorage.getItem("cliente"));

    if (!cliente) {
        // cria estrutura vazia
        cliente = {
            id: null,
            nome: "",
            isAdmin: false,
        };

        localStorage.setItem("cliente", JSON.stringify(cliente));
    }
});