// For an introduction to the Page Control template, see the following documentation:
// http://go.microsoft.com/fwlink/?LinkId=232511
(function () {
    "use strict";

    WinJS.UI.Pages.define("/pages/page1/page1.html", {
        // This function is called whenever a user navigates to this page. It
        // populates the page elements with the app's data.
        ready: function (element, options) {
            // TODO: Initialize the page here.
            WinJS.Utilities.query(".nav").listen("click", linkClickEventHandler, false);

            start();

        },

        unload: function () {
            // TODO: Respond to navigations away from this page.
        },

        updateLayout: function (element) {
            /// <param name="element" domElement="true" />

            // TODO: Respond to changes in layout.
        }
    });


    function linkClickEventHandler(eventInfo) {
        eventInfo.preventDefault();
        var link = eventInfo.target;
        WinJS.Navigation.navigate(link.href);
    }


    function start() {
        var c = new Windows.Web.Http.HttpClient();

        c.getAsync(new Windows.Foundation.Uri("http://cs419recycles.appspot.com/v.1.0/categories")).done(function (result) {
            //document.getElementById('outputField').textContent = result.content;


            var jsonResult = JSON.parse(result.content.toString());

            var line_break = document.createElement("br");
            var test = jsonResult.Category;
            var newjson = JSON.stringify(jsonResult);
            var num = Object.keys(jsonResult.Category).length;
            var i, buttonsToCreate, buttonContainer, newButton;

            buttonContainer = document.getElementById('MyButtons');

            var sortable_list = [];
            for (i = 0; i < num; i++) {
                sortable_list[i] = jsonResult.Category[i];
            }
            sortable_list.sort();



            for (i = 0; i < num; i++) {
                newButton = document.createElement('input');
                newButton.type = 'button';


                newButton.value = sortable_list[i];
                newButton.id = i;
                var line_break = document.createElement("br");
                buttonContainer.appendChild(newButton);
                buttonContainer.appendChild(line_break);

                newButton.onclick = function () {
                    var value_of_button = this.value;
                    create_local_variable(value_of_button);

                };
            }
        })



    }
    function create_local_variable(value_of_button) {
        //document.getElementById('outputField').textContent = value_of_button;

        var file_string = JSON.stringify({ "category_name": value_of_button, "business": "" })

        var local_folder = Windows.Storage.ApplicationData.current.localFolder;

        var filename = "local_variable.txt";
        local_folder.createFileAsync(filename, Windows.Storage.CreationCollisionOption.replaceExisting).then(function (file) {
            return Windows.Storage.FileIO.writeTextAsync(file, file_string);
        }).done(function () {
            WinJS.Navigation.navigate("/pages/page2/page2.html", "test value");
        });

    }


})();
