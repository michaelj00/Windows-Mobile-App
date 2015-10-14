// For an introduction to the Page Control template, see the following documentation:
// http://go.microsoft.com/fwlink/?LinkId=232511


(function () {
    "use strict";

    WinJS.UI.Pages.define("/pages/page3/page3.html", {
        // This function is called whenever a user navigates to this page. It
        // populates the page elements with the app's data.
        ready: function (element, options) {
            ReadFiles();
        },

        unload: function () {
            // TODO: Respond to navigations away from this page.
        },

        updateLayout: function (element) {
            /// <param name="element" domElement="true" />

            // TODO: Respond to changes in layout.
        }

    });


    /*
	    ReadFiles()
		Pulls the stored information for the business selected. 
		
	    Args:		None
	    Returns:	None
	    Calls:		get_business_data()

    */
    function ReadFiles() {
        var filename = "local_variable.txt";
        var localFolder = Windows.Storage.ApplicationData.current.localFolder;

        /*  
            Get local folder.
            Business that the user selected will be stored here. 
        */
        localFolder.getFileAsync(filename).then(function (file) {
            return Windows.Storage.FileIO.readTextAsync(file);
        }).done(function (text) {
            if (text) {

                get_business_data(text);

            }
            else {
                //  This catches the case when the write doesn't happen quickly enough
                //      on the prior page. Redirect it to try again.

                WinJS.Navigation.navigate("/pages/page3/page3.html", "test value");
            }
        }
            );
    }

    /*
	    get_business_data()
		Parses out business from stored file response and makes async call to API on business. 
		
	    Args:		text
	    Returns:	None
	    Calls:		None
    */
    function get_business_data(text) {
        var jsonResult1 = JSON.parse(text);
        var category_name = jsonResult1.category_name;
        var business = jsonResult1.business;

        var c = new Windows.Web.Http.HttpClient();
        var encoded_business_name = encodeURIComponent(business);
        var business_name_without_2f = encoded_business_name.replace(/%2F/g, "%25F");


        c.getAsync(new Windows.Foundation.Uri("http://cs419recycles.appspot.com/v.1.0/business/" + business_name_without_2f)).done(function (result) {

            //http://stackoverflow.com/questions/4295386/how-can-i-check-if-a-value-is-a-json-object
            try {
                var jsonResult = JSON.parse(result.content);
                var line_break = document.createElement("br");
                var buttonContainer, newP;
                var latitude = jsonResult.bus_lat;
                var longitude = jsonResult.bus_long;

                //Create business name in HTML page
                buttonContainer = document.getElementById('BusName');
                newP = document.createElement('p');
                newP.innerHTML = jsonResult.bus_name;
                newP.style.fontSize = "30px";
                buttonContainer.appendChild(newP);

                //Create Business phone number in HTML page
                buttonContainer = document.getElementById('BusPhone');
                newP = document.createElement('p');
                newP.innerHTML = "Phone: " + jsonResult.bus_phone;
                buttonContainer.appendChild(newP);

                //Simple test to see if phone number is entered. If not call button will not generate.
                //API will only return "n/a" or phone number.
                if (jsonResult.bus_phone != "n/a") {
                    //Create a button to call the business. 
                    buttonContainer = document.getElementById('DialBus');
                    newP = document.createElement('p');
                    newP.innerHTML = "Click to Call Business";
                    newP.style.color = "white";
                    newP.style.backgroundColor = "blue";
                    newP.onclick = function () {

                        //http://stackoverflow.com/questions/23797559/wp-8-1-runtime-code-to-make-phone-call-send-sms-send-email-not-the-silverlig?lq=1
                        var phoneTask = Windows.ApplicationModel.Calls.PhoneCallManager.showPhoneCallUI(jsonResult.bus_phone, jsonResult.bus_name);

                    };
                    buttonContainer.appendChild(newP);
                }

                //Create Business Days in HTML page
                buttonContainer = document.getElementById('BusDays');
                newP = document.createElement('p');
                newP.innerHTML = "Days: " + jsonResult.bus_days;
                buttonContainer.appendChild(newP);

                //Create Business Hours in HTML page
                buttonContainer = document.getElementById('BusHours');
                newP = document.createElement('p');
                newP.innerHTML = "Hours: " + jsonResult.bus_hours;
                buttonContainer.appendChild(newP);

                //Create Business URL in HTML page
                buttonContainer = document.getElementById('BusURL');
                newP = document.createElement('p');
                newP.innerHTML = "URL: " + jsonResult.bus_url;
                newP.style.textDecoration = "underline";

                // If no url will not allow clicking of link
                if (jsonResult.bus_url != "n/a") {
                    newP.onclick = function () {
                        location.href = jsonResult.bus_url;
                    }
                }
                buttonContainer.appendChild(newP);

                //Create Business Address in HTML page
                buttonContainer = document.getElementById('BusAddress');
                newP = document.createElement('p');
                newP.innerHTML = "Address: " + jsonResult.bus_address;
                buttonContainer.appendChild(newP);


                //If valid Lat and long were sent: 
                //Send lat and long through the URL to the map iframe for direct parsing there. 
                if ((latitude) && (longitude)) {
                    if ((!isNaN(latitude)) && (!isNaN(longitude))) {
                        var textLatLong = latitude + "&" + longitude;
                        //  Creates URL for iframe map. URL is how latitude and longitude is passed. 
                        document.getElementById('locationSection').innerHTML = "Location";
                        document.getElementById("map").src = "ms-appx-web:///pages/page3/map.html?seed=" + textLatLong;
                    }
                }

            }
            catch (err) {
                var err_response = "That business was not found";
                buttonContainer = document.getElementById('MyOutput');
                var newButton = document.createElement('input');
                newButton.type = 'button';
                newButton.value = err_response;
                buttonContainer.appendChild(newButton);
            }
        })  //End async Get 
    }   //End get_business_data
})();
