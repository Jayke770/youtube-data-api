import fetch from 'node-fetch'
const vidID = 'b80eLC0lHc4'
const api_token = 'AIzaSyAgohf7PXn5xwfZV0e5nwu_ErHrjJMrGQI'
let next_page = true, next_token = undefined, comments = []
async function getComments(token) {
    let data, api
    if (token) {
        api = `https://www.googleapis.com/youtube/v3/commentThreads?key=${api_token}&part=snippet&videoId=${vidID}&maxResults=100&pageToken=${token}`
    } else {
        api = `https://www.googleapis.com/youtube/v3/commentThreads?key=${api_token}&part=snippet&videoId=${vidID}&maxResults=100`
    }

    await fetch(api).then(async (req) => {
        if (req.ok) {
            const res = await req.json()
            data = res
        } else {
            data = `${req.status} ${req.statusText}`
        }
    }).catch((e) => {
        data = e
    })
    return data
}

while (next_page) {
    const data = await getComments(next_token)
    if (data.nextPageToken) {
        next_token = data.nextPageToken
        comments.push(...data.items)
    } else {
        comments.push(...data.items)
        next_page = false
    }
}