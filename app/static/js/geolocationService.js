// export function geolocateUser(onSuccess, onError) {

//     if (navigator.geolocation) {
//         navigator.geolocation.getCurrentPosition(
//             (position) => {
//                 const { latitude, longitude } = position.coords;

//                 console.log('Sending latitude and longitude:', { latitude, longitude });

//                 // Fetch planetary hour data
//                 fetch('/api/geolocation_ephemeris', {

//                     method: 'POST',
//                     headers: { 'Content-Type': 'application/json' },
//                     body: JSON.stringify({ latitude, longitude }),
//                 })
//                     .then((response) => response.json())
//                     .then((data) => {
//                         console.log('Geolocation and planetary hour data:', data);
//                         if (onSuccess) onSuccess(data, latitude, longitude);
//                     })
//                     .catch((error) => {
//                         console.error('Error fetching planetary hour data:', error.message);
//                         if (onError) onError(error);
//                     });
//             },
//             (error) => {
//                 console.error('Geolocation error:', error.message);
//                 if (onError) onError(error);
//             }
//         );
//     } else {
//         console.error('Geolocation is not supported by this browser.');
//         if (onError) onError(new Error('Geolocation not supported'));
//     }
// }



// export function geolocateUser(onSuccess, onError) {
//     if (navigator.geolocation) {
//         navigator.geolocation.getCurrentPosition(
//             (position) => {
//                 const { latitude, longitude } = position.coords;
                
//                 fetch('/api/geolocation_ephemeris', {
//                     method: 'POST',
//                     headers: { 'Content-Type': 'application/json' },
//                     body: JSON.stringify({ latitude, longitude }),
//                 })
//                 .then((response) => response.json())
//                 .then((data) => {
//                     console.log('Full data structure:', JSON.stringify(data, null, 2));
//                     // Validate the entire data structure
//                     if (!data || !data.planetary_positions) {
//                         throw new Error('Invalid planetary data structure');
//                     }
                    
//                     // At this point, data.planetary_positions should contain all planets
//                     if (onSuccess) onSuccess(data, latitude, longitude);
//                 })
//                 .catch((error) => {
//                     console.error('Error fetching planetary hour data:', error.message);
//                     if (onError) onError(error);
//                 });
//             },
//             (error) => {
//                 console.error('Geolocation error:', error.message);
//                 if (onError) onError(error);
//             }
//         );
//     } else {
//         console.error('Geolocation is not supported by this browser.');
//         if (onError) onError(new Error('Geolocation not supported'));
//     }
// }

export function geolocateUser(onSuccess, onError) {
    console.log('🌍 Starting geolocation...');
    const geoStartTime = performance.now();
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                console.log(`📍 Geolocation obtained in ${(performance.now() - geoStartTime).toFixed(0)}ms`);
                const { latitude, longitude } = position.coords;
                
                console.log('Sending coordinates:', { latitude, longitude });
                const apiStartTime = performance.now();
                
                fetch('/api/geolocation_ephemeris', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ latitude, longitude }),
                })
                .then((response) => {
                    console.log(`📡 API response received in ${(performance.now() - apiStartTime).toFixed(0)}ms`);
                    console.log('Response status:', response.status);
                    return response.json();
                })
                .then((data) => {
                    console.log(`📊 API data parsed in ${(performance.now() - apiStartTime).toFixed(0)}ms`);
                    console.log('Raw response data:', data);
                    // Log structure to understand what we're getting
                    console.log('Data keys:', Object.keys(data));
                    

                    // Update validation to match the Flask response structure
                    if (!data?.neo4j_data?.hour) {
                        throw new Error('Invalid data structure - missing hour data');
                    }
                    
                    console.log(`✅ Geolocation service complete in ${(performance.now() - geoStartTime).toFixed(0)}ms`);
                    if (onSuccess) onSuccess(data, latitude, longitude);
                })
                .catch((error) => {
                    console.error('Detailed error:', error);
                    if (onError) onError(error);
                });
            },
            (error) => {
                console.log(`❌ Geolocation failed after ${(performance.now() - geoStartTime).toFixed(0)}ms: ${error.message}`);
                console.error('Geolocation error:', error.message);
                if (onError) onError(error);
            },
            {
                enableHighAccuracy: true,   // Force fresh GPS reading
                timeout: 15000,             // 15 second timeout
                maximumAge: 0               // Don't use cached location - force fresh
            }
        );
    } else {
        console.error('Geolocation is not supported by this browser.');
        if (onError) onError(new Error('Geolocation not supported'));
    }
}