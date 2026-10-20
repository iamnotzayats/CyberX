document.addEventListener('DOMContentLoaded', () => {
    // ==========================================
    // ЛОГИКА МОДАЛЬНОГО ОКНА ВХОДА
    // ==========================================
    const authModal = document.getElementById('auth-modal');
    const authForm = document.getElementById('auth-form');
    const authError = document.getElementById('auth-error');

    window.openAuthModal = function() {
        if (authModal) {
            authModal.classList.add('is-open');
            authModal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        }
    };

    window.closeAuthModal = function() {
        if (authModal) {
            authModal.classList.remove('is-open');
            authModal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
            if (authError) authError.textContent = '';
            if (authForm) authForm.reset();
        }
    };

    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            authError.textContent = '';
            const submitBtn = authForm.querySelector('.auth-modal__submit');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'ЗАГРУЗКА...';
            submitBtn.disabled = true;

            const formData = new FormData(authForm);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            try {
                const response = await fetch('/ajax/login/', {
                    method: 'POST',
                    body: JSON.stringify({
                        username: formData.get('username'),
                        password: formData.get('password')
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                });

                const data = await response.json();

                if (response.ok && data.status === 'ok') {
                    window.location.reload();
                } else {
                    authError.textContent = data.message || 'ОШИБКА ВХОДА';
                    const windowEl = document.querySelector('#auth-modal .auth-modal__window');
                    windowEl.style.animation = 'shake 0.4s steps(3)';
                    setTimeout(() => windowEl.style.animation = '', 400);
                }
            } catch (error) {
                authError.textContent = 'ОШИБКА СОЕДИНЕНИЯ';
            } finally {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // ==========================================
    // ЛОГИКА МОДАЛЬНОГО ОКНА РЕГИСТРАЦИИ
    // ==========================================
    const registerModal = document.getElementById('register-modal');
    const registerForm = document.getElementById('register-form');
    const registerError = document.getElementById('register-error');

    window.openRegisterModal = function() {
        if (registerModal) {
            registerModal.classList.add('is-open');
            registerModal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        }
    };

    window.closeRegisterModal = function() {
        if (registerModal) {
            registerModal.classList.remove('is-open');
            registerModal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
            if (registerError) registerError.textContent = '';
            if (registerForm) registerForm.reset();
        }
    };

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            registerError.textContent = '';
            const submitBtn = registerForm.querySelector('.auth-modal__submit');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'ЗАГРУЗКА...';
            submitBtn.disabled = true;

            const formData = new FormData(registerForm);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            try {
                const response = await fetch('/ajax/register/', {
                    method: 'POST',
                    body: JSON.stringify({
                        username: formData.get('username'),
                        email: formData.get('email'),
                        password: formData.get('password'),
                        password_confirm: formData.get('password_confirm')
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                });

                const data = await response.json();

                if (response.ok && data.status === 'ok') {
                    window.location.reload();
                } else {
                    registerError.textContent = data.message || 'ОШИБКА РЕГИСТРАЦИИ';
                    const windowEl = document.querySelector('#register-modal .auth-modal__window');
                    windowEl.style.animation = 'shake 0.4s steps(3)';
                    setTimeout(() => windowEl.style.animation = '', 400);
                }
            } catch (error) {
                registerError.textContent = 'ОШИБКА СОЕДИНЕНИЯ';
            } finally {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // Закрытие по Esc (для обоих окон)
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (authModal && authModal.classList.contains('is-open')) window.closeAuthModal();
            if (registerModal && registerModal.classList.contains('is-open')) window.closeRegisterModal();
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const forgotModal = document.getElementById('forgot-modal');
    const forgotForm = document.getElementById('forgot-form');
    const forgotError = document.getElementById('forgot-error');
    const forgotSuccess = document.getElementById('forgot-success');

    window.openForgotModal = function() {
        if (forgotModal) {
            forgotModal.classList.add('is-open');
            forgotModal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        }
    };

    window.closeForgotModal = function() {
        if (forgotModal) {
            forgotModal.classList.remove('is-open');
            forgotModal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
            if (forgotError) forgotError.textContent = '';
            if (forgotSuccess) forgotSuccess.style.display = 'none';
            if (forgotForm) forgotForm.reset();
        }
    };

    if (forgotForm) {
        forgotForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            forgotError.textContent = '';
            forgotSuccess.style.display = 'none';
            const submitBtn = document.getElementById('forgot-submit');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'ОТПРАВКА...';
            submitBtn.disabled = true;

            const formData = new FormData(forgotForm);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            try {
                const response = await fetch('/ajax/password-reset/', {
                    method: 'POST',
                    body: JSON.stringify({ email: formData.get('email') }),
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                });

                const data = await response.json();

                if (response.ok && data.status === 'ok') {
                    forgotSuccess.style.display = 'block';
                    forgotSuccess.textContent = 'ПИСЬМО ОТПРАВЛЕНО! ПРОВЕРЬТЕ ПОЧТУ.';
                    forgotForm.reset();
                } else {
                    forgotError.textContent = data.message || 'ОШИБКА';
                }
            } catch (error) {
                forgotError.textContent = 'ОШИБКА СОЕДИНЕНИЯ';
            } finally {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }
});