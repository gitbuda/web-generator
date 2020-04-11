# Simple Static Web Generator

```bash
python generator.py --help
```

An example of the descriptor.yaml file is below.

```yaml
base_url: http://web-site.com
templates_directory: asset/template/
site_directory: site/

index:
    index_template: index.html # Relative to the templates_directory.
copy:
    files:
        #- [src_path, dst_path] # dst_path is relative to the site_directory.
        - [asset/image/image.jpg, images/image.jpg]
        - [asset/style/style.css, style/style.css]
blog:
    posts_content_directory: content
    post_template: post.html # Relative to the templates_directory.
    posts:
        - title: Blog post title
          id: blog_post_unique_id # Used as a path segment.
          directory: YYYY/MM/DD
          artefacts:
              - images/image.jpg

        - title: Another blog post title
          url: https://external-link.com
          # If url field exists everything else except title will be ignored.
```
