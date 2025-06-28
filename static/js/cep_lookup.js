// seu_app/static/js/cep_lookup.js

document.addEventListener('DOMContentLoaded', function () {
    const cepInput = document.querySelector('input[name="cep"]');
    if (!cepInput) return;

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = 'Buscar endereço pelo CEP';
    btn.classList.add('btn', 'btn-info', 'cep-lookup-btn'); 


    const buttonWrapper = document.createElement('div');
    buttonWrapper.classList.add('cep-button-wrapper'); 
    buttonWrapper.appendChild(btn);

    const cepFieldWrapper = cepInput.closest('.form-row') || cepInput.parentNode;

    if (cepInput.nextSibling) {
        cepInput.parentNode.insertBefore(buttonWrapper, cepInput.nextSibling);
    } else {
        cepInput.parentNode.appendChild(buttonWrapper);
    }


    btn.addEventListener('click', function () {
        const cep = cepInput.value.replace(/\D/g, '');

        if (cep.length !== 8) {
            mostrarErro("Digite um CEP com 8 dígitos.");
            return;
        }

        fetch(`https://viacep.com.br/ws/${cep}/json/`)
            .then(resp => resp.json())
            .then(data => {
                if (data.erro) {
                    mostrarErro("CEP não encontrado.");
                    return;
                }

                document.querySelector('input[name="endereco"]').value = data.logradouro || '';
                document.querySelector('input[name="cidade"]').value = data.localidade || '';
                document.querySelector('input[name="estado"]').value = data.uf || '';
                limparErro();
            })
            .catch(() => {
                mostrarErro("Erro ao buscar o CEP.");
            });
    });

    function mostrarErro(msg) {
        let errorDiv = document.getElementById('cep-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'cep-error';
            errorDiv.style.color = 'red';
            cepInput.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = msg;
    }

    function limparErro() {
        const errorDiv = document.getElementById('cep-error');
        if (errorDiv) errorDiv.remove();
    }
});