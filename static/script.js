$("document").ready(function() {
    // Load Header
    $("header").load("/static/assets/navbar.html", function() {
        $(".navbar-nav")
            .find("a").each(function() {
                // https://stackoverflow.com/questions/406192/get-current-url-with-jquery#406208
                // If it leads to 'this' link, make active
                if ($(this).attr("href") === window.location.pathname){
                    $(this).addClass("active");
                    // Change href to "/"
                    $(this).removeAttr("href")
                }
            });
    });

    // Load Footer
    $("footer").load("/static/assets/footer.html");
})


