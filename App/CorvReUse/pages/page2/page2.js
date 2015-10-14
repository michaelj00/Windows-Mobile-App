// For an introduction to the Page Control template, see the following documentation:
// http://go.microsoft.com/fwlink/?LinkId=232511
(function () {
    "use strict";

    WinJS.UI.Pages.define("/pages/page2/page2.html", {
        // This function is called whenever a user navigates to this page. It
        // populates the page elements with the app's data.
        ready: function (element, options) {
            // TODO: Initialize the page here.
            WinJS.Utilities.query(".nav").listen("click", linkClickEventHandler, false);

            ReadFiles();
        },

    });


    function linkClickEventHandler(eventInfo) {
        eventInfo.preventDefault();
        var link = eventInfo.target;
        WinJS.Navigation.navigate(link.href);
    }

    /*
    ReadFiles()
    ReadFiles will open local_variable.txt and pull out the category_name

    Args:		None
    Returns:	None
    Calls:		get_category_info()
*/

    function ReadFiles() {
        var filename = "local_variable.txt";
        var localFolder = Windows.Storage.ApplicationData.current.localFolder;

        /*  
            Get local folder.
            Category that the user selected will be stored here. 
        */
        localFolder.getFileAsync(filename).then(function (file) {
            return Windows.Storage.FileIO.readTextAsync(file);
        }).done(function (text) {
            if (text) {
                get_category_info(text);
            }
            else {
                //  This catches the case when the write doesn't happen quickly enough
                //      on the prior page.
                WinJS.Navigation.navigate("/pages/page2/page2.html", "test value");
            }
        }
            );
    }

    function get_category_info(text) {

        var jsonResult1 = JSON.parse(text);
        var category_name = jsonResult1.category_name;
        var business = jsonResult1.business;
        /*
                script to pull businesses that link to the 
                category.
        */
        var c = new Windows.Web.Http.HttpClient();
        var encoded_category_name = encodeURIComponent(category_name);
        var category_name_without_2f = encoded_category_name.replace(/%2F/g, "%25F");


        c.getAsync(new Windows.Foundation.Uri("http://cs419recycles.appspot.com/v.1.0/categories/" + category_name_without_2f)).done(function (result) {
            //http://stackoverflow.com/questions/4295386/how-can-i-check-if-a-value-is-a-json-object

            try {
                var jsonResult = JSON.parse(result.content);
                var itemNum = Object.keys(JSON.parse(result.content).Items).length;

                //Prints items examples of category if any exist.
                //If none exist default to no printing
                if (itemNum != 0) {
                    document.getElementById("items").innerHTML = "Examples: ";
                    for (i = 0; i < itemNum - 1; i++) {
                        document.getElementById('items').innerHTML += jsonResult.Items[i];
                        document.getElementById('items').innerHTML += ", ";
                    }
                    document.getElementById('items').innerHTML += jsonResult.Items[itemNum - 1];
                }
            }
            catch (err) {
                document.getElementById("items").innerHTML = "Examples: None";
            }
            try {
                var jsonResult = JSON.parse(result.content);
                var line_break = document.createElement("br");
                var test = jsonResult.Business;
                var newjson = JSON.stringify(jsonResult);
                var num = Object.keys(jsonResult.Business).length;
                var itemNum = Object.keys(jsonResult.Items).length;
                var i, buttonsToCreate, buttonContainer, newButton;

                //Creates non-clickable button that no business recycles
                //the category if businesses returned are 0
                if (num == 0) {
                    document.getElementById('catName').innerHTML = category_name;
                    var err_response = "No business recycles this category";
                    buttonContainer = document.getElementById('MyButtons');
                    var newButton = document.createElement('input');
                    newButton.type = 'button';
                    newButton.value = err_response;
                    buttonContainer.appendChild(newButton);

                } else {
                    //Default case where businesses do recycle a category and 
                    //creates buttons for each.

                    var sortable_list = [];
                    for (i = 0; i < num; i++) {
                        sortable_list[i] = jsonResult.Business[i];
                    }
                    sortable_list.sort();



                    buttonContainer = document.getElementById('MyButtons');
                    document.getElementById('catName').innerHTML = category_name;

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
                            create_local_variable(value_of_button, category_name);
                        };
                    }
                }
            }
            catch (err) {
                //  Database returned a non-json value
                var err_response = "No business recycles this category";
                buttonContainer = document.getElementById('MyButtons');
                var newButton = document.createElement('input');
                newButton.type = 'button';
                newButton.value = err_response;
                buttonContainer.appendChild(newButton);
            }

        })



    }

    function create_local_variable(value_of_button, category_name, business) {

        var file_string = JSON.stringify({ "category_name": category_name, "business": value_of_button })
        var local_folder = Windows.Storage.ApplicationData.current.localFolder;
        var filename = "local_variable.txt";

        //  Create File with content file_string. Overwrite existing file.
        local_folder.createFileAsync(filename, Windows.Storage.CreationCollisionOption.replaceExisting).then(function (file) {
            return Windows.Storage.FileIO.writeTextAsync(file, file_string);
        }).done(function () {
            // Write complete redirect to page 3
            WinJS.Navigation.navigate("/pages/page3/page3.html", "test value");
        });

    }

})();
