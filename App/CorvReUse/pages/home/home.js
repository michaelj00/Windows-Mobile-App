(function () {
    "use strict";

    WinJS.UI.Pages.define("/pages/home/home.html", {
        // This function is called whenever a user navigates to this page. It
        // populates the page elements with the app's data.
        ready: function (element, options) {
            // TODO: Initialize the page here            

            //  Navigate to page1 (main page that will list categories)
            document.querySelector("#Go_page1").onclick = function (args) {

                WinJS.Navigation.navigate("/pages/page1/page1.html", "test value");


            };
        }
    });

    //function if needed to test connectivity. Can not get emulator to successfully turn 
    //off data to test. 
    function test_connectivity() {
        var networkInfo = Windows.Networking.Connectivity.NetworkInformation;
        var connectionProfile = networkInfo.getInternetConnectionProfile();

        if (connectionProfile == null) {
            var line_break = document.createElement("br");
            var newButton, buttonContainer;

            buttonContainer = document.getElementById('outputField');
            newButton = document.createElement('p');
            newButton.innerHTML = "An active internet connection could not be found. Please connect to the internet to proceed.";
            buttonContainer.appendChild(newButton);
            buttonContainer.appendChild(line_break);
        } else {
            //internet connection exists allow move to category page.
            //WinJS.Navigation.navigate("/pages/page1/page1.html", "test value");
            var line_break = document.createElement("br");
            var newButton, buttonContainer;

            buttonContainer = document.getElementById('outputField');
            newButton = document.createElement('p');
            newButton.innerHTML = "Inter.";
            buttonContainer.appendChild(newButton);
            buttonContainer.appendChild(line_break);
        }
    }
})();
