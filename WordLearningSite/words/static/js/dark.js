document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('toggle-dark-mode');
    const darkStylesheet = document.getElementById('dark-mode-stylesheet'); // 다크 모드 CSS 파일

    if (toggleButton) {
        // 다크 모드 상태 확인
        if (localStorage.getItem('dark-mode') === 'enabled') {
            document.body.classList.add('dark-mode');
            darkStylesheet.removeAttribute('disabled'); // 다크 모드 CSS 활성화
            const icon = toggleButton.querySelector('i');
            icon.classList.toggle('fa-moon');
            icon.classList.toggle('fa-sun');
        }

        // 다크 모드 토글
        toggleButton.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');

            // 다크 모드 CSS 활성화/비활성화
            if (document.body.classList.contains('dark-mode')) {
                darkStylesheet.removeAttribute('disabled');
                localStorage.setItem('dark-mode', 'enabled');
            } else {
                darkStylesheet.setAttribute('disabled', 'true');
                localStorage.removeItem('dark-mode');
            }

            // 아이콘 변경
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-moon');
            icon.classList.toggle('fa-sun');
        });
    }
});
