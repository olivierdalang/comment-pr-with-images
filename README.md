# Attach image to comment

Comment with image is a GitHub Action that takes a list of images,
uploads them to an [Image Upload Service](#available-image-upload-services) and
**comments** the screenshots on the **pull request** that **triggered** the action.

It was adapted from https://github.com/saadmk11/comment-webpage-screenshot, mostly to strip down the screenshot feature.

**Note:** This Action Only Works on Pull Requests.

## Workflow inputs

These are the inputs that can be provided on the workflow.

| Name | Required | Description | Default |
|------|----------|-------------|---------|
| `upload_to` | No | Image Upload Service Name (Options are: `github_branch`, `imgur`) **[More Details](#available-image-upload-services)** | `github_branch` |
| `images` | Yes | Comma separated lists of artifacts to upload (supports glob patterns: `tests_artifacts/**/*.gif, tests_artifacts/**/*.png`) | `null` |
| `github_token` | No | `GITHUB_TOKEN` provided by the workflow run or Personal Access Token (PAT) | `github.token` |

## Example Workflow

```yaml
name: Comment Webpage Screenshot

on:
  pull_request:
    types: [opened, reopened, synchronize]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Some step that generates image.png and actions.gif under ./artifacts
        run: ...

      - name: Comment Webpage Screenshot
        uses: opengisch/comment-pr-with-images@upload_only
        with:
          # Optional, the action will create a new branch and
          # upload the screenshots to that branch.
          upload_to: github_branch  # Or, imgur
          # Comma seperated list of files to upload.
          images: "tests_artifacts/**/*.gif, tests_artifacts/**/*.png"
          # Optional
          github_token: {{ secrets.MY_GITHUB_TOKEN }}
```


## Available Image Upload Services

**As GitHub Does not allow us to upload images to a comment using the API
we need to rely on other services to host the screenshots.**

These are the currently available image upload services.

### Imgur

If the value of `upload_to` input is `imgur` then the screenshots will be uploaded to Imgur.
Keep in mind that the uploaded screenshots will be **public** and anyone can see them.
Imgur also has a rate limit of how many images can be uploaded per hour.
Refer to Imgur's [Rate Limits](https://api.imgur.com/#limits) Docs for more details.
This is suitable for **small open source** repositories.

Please refer to Imgur terms of service [here](https://imgur.com/tos)

### GitHub Branch (Default)

If the value of `upload_to` input is `github_branch` then the screenshots will be pushed
to a GitHub branch created by the action on your repository.
The screenshots on the comments will reference the Images pushed to this branch.

This is suitable for **open source** and **private** repositories.

**If you want to add/use a different image upload service, feel free create a new issue/pull request.**

# License

The code in this project is released under the [GNU GENERAL PUBLIC LICENSE Version 3](LICENSE).
