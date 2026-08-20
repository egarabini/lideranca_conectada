(function () {
    var form = document.getElementById('lp-form');
    var submitBtn = document.getElementById('lp-submit');
    var successBox = document.getElementById('lp-success');

    if (!form) return;

    var whatsappInput = document.getElementById('whatsapp');

    whatsappInput.addEventListener('input', function (e) {
        var v = e.target.value.replace(/\D/g, '');
        if (v.length > 11) v = v.substring(0, 11);
        if (v.length > 6) {
            e.target.value = '(' + v.substring(0, 2) + ') ' + v.substring(2, 7) + '-' + v.substring(7);
        } else if (v.length > 2) {
            e.target.value = '(' + v.substring(0, 2) + ') ' + v.substring(2);
        } else if (v.length > 0) {
            e.target.value = '(' + v;
        }
    });

    function addErrorElements() {
        var fields = form.querySelectorAll('.lp-field');
        for (var i = 0; i < fields.length; i++) {
            if (!fields[i].querySelector('.lp-error')) {
                var span = document.createElement('span');
                span.className = 'lp-error';
                fields[i].appendChild(span);
            }
        }
    }

    addErrorElements();

    function clearErrors() {
        var fields = form.querySelectorAll('.lp-field');
        for (var i = 0; i < fields.length; i++) {
            fields[i].classList.remove('has-error');
        }
    }

    function showFieldError(fieldId, message) {
        var field = document.getElementById(fieldId);
        if (!field) return;
        var wrapper = field.closest('.lp-field');
        if (!wrapper) return;
        wrapper.classList.add('has-error');
        var errorEl = wrapper.querySelector('.lp-error');
        if (errorEl) errorEl.textContent = message;
    }

    function validateForm() {
        clearErrors();
        var valid = true;

        var nome = document.getElementById('nome').value.trim();
        if (nome.length < 2) { showFieldError('nome', 'Informe seu nome completo'); valid = false; }

        var email = document.getElementById('email').value.trim();
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { showFieldError('email', 'Informe um e-mail válido'); valid = false; }

        var wpp = document.getElementById('whatsapp').value.replace(/\D/g, '');
        if (wpp.length < 10) { showFieldError('whatsapp', 'Informe um WhatsApp válido'); valid = false; }

        var empresa = document.getElementById('empresa').value.trim();
        if (empresa.length < 2) { showFieldError('empresa', 'Informe o nome da empresa'); valid = false; }

        var cargo = document.getElementById('cargo').value.trim();
        if (cargo.length < 2) { showFieldError('cargo', 'Informe seu cargo ou função'); valid = false; }

        var colab = document.getElementById('colaboradores').value;
        if (!colab) { showFieldError('colaboradores', 'Selecione o número de colaboradores'); valid = false; }

        return valid;
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (!validateForm()) return;

        submitBtn.disabled = true;
        submitBtn.textContent = 'Enviando...';

        var data = {
            nome: document.getElementById('nome').value.trim(),
            email: document.getElementById('email').value.trim(),
            whatsapp: document.getElementById('whatsapp').value.trim(),
            empresa: document.getElementById('empresa').value.trim(),
            cargo: document.getElementById('cargo').value.trim(),
            colaboradores: document.getElementById('colaboradores').value,
            cidade_uf: document.getElementById('cidade_uf').value.trim()
        };

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/leads', true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        xhr.onreadystatechange = function () {
            if (xhr.readyState !== 4) return;
            submitBtn.disabled = false;
            submitBtn.textContent = 'Quero agendar uma conversa';

            if (xhr.status >= 200 && xhr.status < 300) {
                var resp = null;
                try { resp = JSON.parse(xhr.responseText); } catch (ex) {}
                if (resp && resp.redirect) {
                    window.location.href = resp.redirect;
                    return;
                }
                form.style.display = 'none';
                successBox.classList.remove('hidden');
            } else {
                try {
                    var resp = JSON.parse(xhr.responseText);
                    if (resp.errors) {
                        for (var i = 0; i < resp.errors.length; i++) {
                            showFieldError(resp.errors[i].field, resp.errors[i].message);
                        }
                    } else {
                        alert('Ocorreu um erro. Tente novamente.');
                    }
                } catch (ex) {
                    alert('Ocorreu um erro. Tente novamente.');
                }
            }
        };

        xhr.onerror = function () {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Quero agendar uma conversa';
            alert('Erro de conexão. Verifique sua internet e tente novamente.');
        };

        xhr.send(JSON.stringify(data));
    });
})();
