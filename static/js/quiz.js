// ================================
// QUIZ INTERACTION & SAFETY LOGIC
// ================================

// Disable right-click & warn on leave during quiz attempt
document.addEventListener("DOMContentLoaded", () => {

    const isQuizAttempt = window.location.pathname.includes("/quiz/attempt/");

    if (isQuizAttempt) {
        // Disable right click
        document.addEventListener("contextmenu", (event) => {
            event.preventDefault();
        });

        // Warn user before leaving quiz
        window.addEventListener("beforeunload", (e) => {
            e.preventDefault();
            e.returnValue = "";
        });
    }

    // ================================
    // SMOOTH SCROLL FOR ANCHOR LINKS
    // ================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (e) {
            const targetId = this.getAttribute("href");

            if (!targetId || targetId === "#") return;

            const target = document.querySelector(targetId);
            if (!target) return;

            e.preventDefault();
            target.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        });
    });

    // ================================
    // AUTO DISMISS ALERTS
    // ================================
    const alerts = document.querySelectorAll(".alert");

    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.transition = "opacity 0.5s ease";
                alert.style.opacity = "0";

                setTimeout(() => {
                    if (alert.parentElement) {
                        alert.remove();
                    }
                }, 500);
            });
        }, 5000);
    }

});
