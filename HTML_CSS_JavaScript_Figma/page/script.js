"use strict";

const html = document.documentElement;
const themeBtn = document.querySelector("#themeToggle");

function applyTheme(theme) {
    html.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
}

applyTheme(localStorage.getItem("theme") || "dark");

themeBtn.addEventListener("click", () => {
    applyTheme(html.getAttribute("data-theme") === "dark" ? "light" : "dark");
});

const goTop = document.querySelector("#goTop");
const headerCta = document.querySelector("#headerCta");
const heroSection = document.querySelector("#hero");

function scrollActions() {
    if (window.scrollY > heroSection.offsetHeight) {
        goTop.classList.add("is-visible");
        headerCta.classList.add("is-visible");
    } else {
        goTop.classList.remove("is-visible");
        headerCta.classList.remove("is-visible");
    }
}

window.addEventListener("scroll", scrollActions);
scrollActions();

goTop.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
});

const hamburger = document.querySelector("#hamburger");
const navDrawer = document.querySelector("#navDrawer");
const navOverlay = document.querySelector("#navOverlay");
const navClose = document.querySelector("#navClose");

function openDrawer() {
    navDrawer.classList.add("is-open");
    navOverlay.classList.add("is-active");
    document.body.style.overflow = "hidden";
    navClose.focus();
}

function closeDrawer() {
    navDrawer.classList.remove("is-open");
    navOverlay.classList.remove("is-active");
    document.body.style.overflow = "";
    hamburger.focus();
}

hamburger.addEventListener("click", openDrawer);
navClose.addEventListener("click", closeDrawer);
navOverlay.addEventListener("click", closeDrawer);

navDrawer
    .querySelectorAll(".nav-drawer__link, .js-modal-open")
    .forEach((el) => {
        el.addEventListener("click", closeDrawer);
    });

const modalOverlay = document.querySelector("#modalOverlay");
const modalClose = document.querySelector("#modalClose");

function openModal() {
    modalOverlay.classList.add("is-open");
    document.body.style.overflow = "hidden";
    modalClose.focus();
}

function closeModal() {
    modalOverlay.classList.remove("is-open");
    document.body.style.overflow = "";
}

document.querySelectorAll(".js-modal-open").forEach((btn) => {
    btn.addEventListener("click", openModal);
});

modalClose.addEventListener("click", closeModal);

modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) closeModal();
});

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && navDrawer.classList.contains("is-open")) {
        closeDrawer();
    } else if (
        e.key === "Escape" &&
        modalOverlay.classList.contains("is-open")
    ) {
        closeModal();
    }
});

const signupForm = document.querySelector("#signupForm");
const formSuccess = signupForm.querySelector("#formSuccess");
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function setField(groupId, valid, msg) {
    const group = signupForm.querySelector(`#${groupId}`);
    if (!group) return;

    const input = group.querySelector(".form__input");
    const err = group.querySelector(".form__error");

    group.classList.toggle("has-error", !valid);

    if (input) {
        input.classList.toggle("is-error", !valid);
        input.classList.toggle("is-valid", valid);
    }
    if (err && msg) err.textContent = msg;
}

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

    signupForm
        .querySelectorAll(".form__group, .btn--full")
        .forEach((el) => (el.style.display = "none"));
    formSuccess.removeAttribute("hidden");
    setTimeout(closeModal, 3000);
});

const billingToggle = document.querySelector("#billingToggle");
const lblMonthly = document.querySelector("#lbl-monthly");
const lblAnnual = document.querySelector("#lbl-annual");

billingToggle.addEventListener("change", () => {
    const annual = billingToggle.checked;
    lblMonthly.classList.toggle("is-active", !annual);
    lblAnnual.classList.toggle("is-active", annual);

    document.querySelectorAll(".plan-card__amount").forEach((el) => {
        el.textContent = annual ? el.dataset.y : el.dataset.m;
    });
});

lblMonthly.classList.add("is-active");

const cookieBar = document.querySelector("#cookieBar");
const cookieAccept = cookieBar.querySelector("#cookieAccept");
const cookieDecline = cookieBar.querySelector("#cookieDecline");

if (localStorage.getItem("cookies")) {
    cookieBar.classList.add("is-hidden");
}

function dismissCookie(choice) {
    cookieBar.classList.add("is-hidden");
    localStorage.setItem("cookies", choice);
}

cookieAccept.addEventListener("click", () => dismissCookie("accepted"));
cookieDecline.addEventListener("click", () => dismissCookie("declined"));

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
