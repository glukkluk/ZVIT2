"use strict";

/* ============================================================
   THEME TOGGLE
   ============================================================ */
const html = document.documentElement;
const themeBtn = document.getElementById("themeToggle");

function applyTheme(theme) {
    html.setAttribute("data-theme", theme);
    localStorage.setItem("fd-theme", theme);
}

applyTheme(localStorage.getItem("fd-theme") || "dark");

themeBtn.addEventListener("click", () => {
    applyTheme(html.getAttribute("data-theme") === "dark" ? "light" : "dark");
});

/* ============================================================
   STICKY HEADER
   ============================================================ */
const header = document.getElementById("header");

window.addEventListener(
    "scroll",
    () => {
        header.classList.toggle("header--scrolled", window.scrollY > 8);
    },
    { passive: true },
);

/* ============================================================
   GO TOP BUTTON
   Show after scrolling past hero height (measured dynamically)
   ============================================================ */
const goTop = document.getElementById("goTop");
const heroSection = document.getElementById("hero");

function updateGoTop() {
    const threshold = heroSection
        ? heroSection.offsetHeight
        : window.innerHeight;
    goTop.classList.toggle("is-visible", window.scrollY > threshold);
}

window.addEventListener("scroll", updateGoTop, { passive: true });
updateGoTop();

goTop.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
});

/* ============================================================
   HAMBURGER / NAV DRAWER
   Opens from the right side
   ============================================================ */
const hamburger = document.getElementById("hamburger");
const navDrawer = document.getElementById("navDrawer");
const navOverlay = document.getElementById("navOverlay");
const navClose = document.getElementById("navClose");

function openDrawer() {
    navDrawer.classList.add("is-open");
    navOverlay.classList.add("is-active");
    hamburger.classList.add("is-active");
    hamburger.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
    navClose.focus();
}

function closeDrawer() {
    navDrawer.classList.remove("is-open");
    navOverlay.classList.remove("is-active");
    hamburger.classList.remove("is-active");
    hamburger.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
    hamburger.focus();
}

hamburger.addEventListener("click", openDrawer);
navClose.addEventListener("click", closeDrawer);
navOverlay.addEventListener("click", closeDrawer);

// Close on any drawer link click
navDrawer
    .querySelectorAll(".nav-drawer__link, .js-modal-open")
    .forEach((el) => {
        el.addEventListener("click", closeDrawer);
    });

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && navDrawer.classList.contains("is-open"))
        closeDrawer();
});

/* ============================================================
   MODAL WINDOW
   ============================================================ */
const modalOverlay = document.getElementById("modalOverlay");
const modalClose = document.getElementById("modalClose");

function openModal() {
    modalOverlay.classList.add("is-open");
    document.body.style.overflow = "hidden";
    setTimeout(() => modalClose.focus(), 60);
}

function closeModal() {
    modalOverlay.classList.remove("is-open");
    document.body.style.overflow = "";
}

// All triggers that open modal
document.querySelectorAll(".js-modal-open").forEach((btn) => {
    btn.addEventListener("click", openModal);
});

modalClose.addEventListener("click", closeModal);

modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) closeModal();
});

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modalOverlay.classList.contains("is-open"))
        closeModal();
});

/* ============================================================
   FORM — email validation via regex, field-level feedback
   ============================================================ */
const signupForm = document.getElementById("signupForm");
const formSuccess = document.getElementById("formSuccess");
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function setField(groupId, valid, msg) {
    const group = document.getElementById(groupId);
    if (!group) return;
    const input = group.querySelector(".form__input, .form__textarea");
    const err = group.querySelector(".form__error");

    group.classList.toggle("has-error", !valid);
    if (input) {
        input.classList.toggle("is-error", !valid);
        input.classList.toggle("is-valid", valid);
    }
    if (err && msg) err.textContent = msg;
}

// Real-time email feedback
document.getElementById("email").addEventListener("blur", function () {
    if (!this.value) return;
    setField(
        "fg-email",
        EMAIL_RE.test(this.value.trim()),
        "Введіть дійсну email-адресу.",
    );
});

signupForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const firstName = document.getElementById("firstName").value.trim();
    const lastName = document.getElementById("lastName").value.trim();
    const email = document.getElementById("email").value.trim();

    let ok = true;

    if (!firstName) {
        setField("fg-fname", false, "Введіть ваше ім'я.");
        ok = false;
    } else setField("fg-fname", true);

    if (!lastName) {
        setField("fg-lname", false, "Введіть ваше прізвище.");
        ok = false;
    } else setField("fg-lname", true);

    if (!email || !EMAIL_RE.test(email)) {
        setField("fg-email", false, "Введіть дійсну email-адресу.");
        ok = false;
    } else {
        setField("fg-email", true);
    }

    if (!ok) return;

    // Show success
    signupForm
        .querySelectorAll(".form__group, .btn--full")
        .forEach((el) => (el.style.display = "none"));
    formSuccess.removeAttribute("hidden");
    setTimeout(closeModal, 2800);
});

/* ============================================================
   PRICING TOGGLE — monthly / annual
   ============================================================ */
const billingToggle = document.getElementById("billingToggle");
const lblMonthly = document.getElementById("lbl-monthly");
const lblAnnual = document.getElementById("lbl-annual");

billingToggle.addEventListener("change", () => {
    const annual = billingToggle.checked;
    lblMonthly.classList.toggle("is-active", !annual);
    lblAnnual.classList.toggle("is-active", annual);

    document.querySelectorAll(".plan-card__amount").forEach((el) => {
        el.textContent = annual ? el.dataset.y : el.dataset.m;
    });
});

// Set initial active label
lblMonthly.classList.add("is-active");

/* ============================================================
   COOKIE BAR
   Saved to localStorage — hides on revisit
   ============================================================ */
const cookieBar = document.getElementById("cookieBar");
const cookieAccept = document.getElementById("cookieAccept");
const cookieDecline = document.getElementById("cookieDecline");

if (localStorage.getItem("fd-cookie")) {
    cookieBar.classList.add("is-hidden");
}

function dismissCookie(choice) {
    cookieBar.classList.add("is-hidden");
    localStorage.setItem("fd-cookie", choice);
}

cookieAccept.addEventListener("click", () => dismissCookie("accepted"));
cookieDecline.addEventListener("click", () => dismissCookie("declined"));

/* ============================================================
   SCROLL REVEAL — pure IntersectionObserver, no library
   Animations fire on first scroll into view
   ============================================================ */
const revealEls = document.querySelectorAll(".reveal");

const revealObserver = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                revealObserver.unobserve(entry.target);
            }
        });
    },
    { threshold: 0.1, rootMargin: "0px 0px -40px 0px" },
);

revealEls.forEach((el) => revealObserver.observe(el));

/* ============================================================
   SWIPER SLIDER — testimonials
   ============================================================ */
new Swiper(".reviews__swiper", {
    loop: true,
    slidesPerView: 1,
    spaceBetween: 20,
    autoplay: { delay: 5000, disableOnInteraction: false },
    pagination: { el: ".swiper-pagination", clickable: true },
    breakpoints: {
        640: { slidesPerView: 2 },
        1024: { slidesPerView: 3 },
    },
    a11y: {
        prevSlideMessage: "Попередній відгук",
        nextSlideMessage: "Наступний відгук",
    },
});

/* ============================================================
   COUNTDOWN TIMER
   Target: 47 days from page load
   ============================================================ */
const eventDate = new Date();
eventDate.setDate(eventDate.getDate() + 47);
eventDate.setHours(10, 0, 0, 0);

const cdDays = document.getElementById("cd-days");
const cdHours = document.getElementById("cd-hours");
const cdMins = document.getElementById("cd-mins");
const cdSecs = document.getElementById("cd-secs");

function pad(n) {
    return String(n).padStart(2, "0");
}

function tickCountdown() {
    const diff = eventDate - Date.now();

    if (diff <= 0) {
        [cdDays, cdHours, cdMins, cdSecs].forEach(
            (el) => (el.textContent = "00"),
        );
        return;
    }

    cdDays.textContent = pad(Math.floor(diff / 86400000));
    cdHours.textContent = pad(Math.floor((diff % 86400000) / 3600000));
    cdMins.textContent = pad(Math.floor((diff % 3600000) / 60000));
    cdSecs.textContent = pad(Math.floor((diff % 60000) / 1000));
}

tickCountdown();
setInterval(tickCountdown, 1000);

/* ============================================================
   HEADER CTA — show on desktop once scrolled past hero
   ============================================================ */
const headerCta = document.getElementById("headerCta");

if (headerCta && window.innerWidth >= 768) {
    headerCta.style.display = "none";
    window.addEventListener(
        "scroll",
        () => {
            const threshold = heroSection
                ? heroSection.offsetHeight * 0.5
                : 400;
            headerCta.style.display =
                window.scrollY > threshold ? "inline-flex" : "none";
        },
        { passive: true },
    );
}
