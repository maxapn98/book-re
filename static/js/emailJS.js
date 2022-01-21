(function() {
    // https://dashboard.emailjs.com/admin/integration
    emailjs.init('user_bv1Gx2FNcuftJSMKXsD7a');
})();

window.onload = function(){
    let contactForm = document.getElementById("contact-form");
    contactForm.addEventListener("submit", function(event){
        event.preventDefault();
        // Send form to email JS
        emailjs.sendForm('service_0lpf6pe', 'template_ks68e2i', contactForm)
        contactForm.reset();
    });
    
}