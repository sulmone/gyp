{
  'variables': {
    'depth': '..',
  },
  'includes': [
    '../build/common.gypi',
  ],
  'target_defaults': {
    'include_dirs': [
      '..',
    ],
    'vs_props': ['build/net.vsprops'],
  },
  'targets': [
    {
      'target_name': 'net',
      'type': 'static_library',
      'dependencies': [
        'net_resources',
        '../googleurl/build/googleurl.gyp:googleurl',
        '../sdch/sdch.gyp:sdch',
        '../third_party/bzip2/bzip2.gyp:bzip2',
        '../third_party/modp_b64/modp_b64.gyp:modp_b64',
        '../third_party/zlib/zlib.gyp:zlib',
      ],
      'sources': [
        'base/address_list.cc',
        'base/address_list.h',
        'base/auth.h',
        'base/base64.cc',
        'base/base64.h',
        'base/bzip2_filter.cc',
        'base/bzip2_filter.h',
        'base/cert_status_flags.h',
        'base/client_socket.h',
        'base/client_socket_factory.cc',
        'base/client_socket_factory.h',
        'base/client_socket_handle.cc',
        'base/client_socket_handle.h',
        'base/client_socket_pool.cc',
        'base/client_socket_pool.h',
        'base/completion_callback.h',
        'base/connection_type_histograms.cc',
        'base/connection_type_histograms.h',
        'base/cookie_monster.cc',
        'base/cookie_monster.h',
        'base/cookie_policy.cc',
        'base/cookie_policy.h',
        'base/data_url.cc',
        'base/data_url.h',
        'base/directory_lister.cc',
        'base/directory_lister.h',
        'base/dns_resolution_observer.cc',
        'base/dns_resolution_observer.h',
        'base/effective_tld_names.dat',
        'base/escape.cc',
        'base/escape.h',
        'base/ev_root_ca_metadata.cc',
        'base/ev_root_ca_metadata.h',
        'base/file_stream.h',
        'base/file_stream_win.cc',
        'base/filter.cc',
        'base/filter.h',
        'base/gzip_filter.cc',
        'base/gzip_filter.h',
        'base/gzip_header.cc',
        'base/gzip_header.h',
        'base/host_resolver.cc',
        'base/host_resolver.h',
        'base/io_buffer.h',
        'base/listen_socket.cc',
        'base/listen_socket.h',
        'base/load_flags.h',
        'base/mime_sniffer.cc',
        'base/mime_sniffer.h',
        'base/mime_util.cc',
        'base/mime_util.h',
        'base/net_error_list.h',
        'base/net_errors.cc',
        'base/net_errors.h',
        'base/net_module.cc',
        'base/net_module.h',
        'base/net_resources.h',
        'base/net_util.cc',
        'base/net_util.h',
        'base/net_util_win.cc',
        'base/platform_mime_util.h',
        'base/platform_mime_util_win.cc',
        'build/precompiled_net.cc',
        'build/precompiled_net.h',
        'base/registry_controlled_domain.cc',
        'base/registry_controlled_domain.h',
        'base/scoped_cert_chain_context.h',
        'base/sdch_filter.cc',
        'base/sdch_filter.h',
        'base/sdch_manager.cc',
        'base/sdch_manager.h',
        'base/socket.h',
        'base/ssl_client_socket.h',
        'base/ssl_client_socket_win.cc',
        'base/ssl_client_socket_win.h',
        'base/ssl_config_service.cc',
        'base/ssl_config_service.h',
        'base/ssl_info.h',
        'base/ssl_test_util.cc',
        'base/tcp_client_socket.h',
        'base/tcp_client_socket_win.cc',
        'base/telnet_server.cc',
        'base/telnet_server.h',
        'base/upload_data.cc',
        'base/upload_data.h',
        'base/upload_data_stream.cc',
        'base/upload_data_stream.h',
        'base/wininet_util.cc',
        'base/wininet_util.h',
        'base/winsock_init.cc',
        'base/winsock_init.h',
        'base/x509_certificate.cc',
        'base/x509_certificate.h',
        'base/x509_certificate_win.cc',
        'url_request/mime_sniffer_proxy.cc',
        'url_request/mime_sniffer_proxy.h',
        'url_request/url_request.cc',
        'url_request/url_request.h',
        'url_request/url_request_about_job.cc',
        'url_request/url_request_about_job.h',
        'url_request/url_request_context.h',
        'url_request/url_request_error_job.cc',
        'url_request/url_request_error_job.h',
        'url_request/url_request_file_dir_job.cc',
        'url_request/url_request_file_dir_job.h',
        'url_request/url_request_file_job.cc',
        'url_request/url_request_file_job.h',
        'url_request/url_request_filter.cc',
        'url_request/url_request_filter.h',
        'url_request/url_request_ftp_job.cc',
        'url_request/url_request_ftp_job.h',
        'url_request/url_request_http_job.cc',
        'url_request/url_request_http_job.h',
        'url_request/url_request_inet_job.cc',
        'url_request/url_request_inet_job.h',
        'url_request/url_request_job.cc',
        'url_request/url_request_job.h',
        'url_request/url_request_job_manager.cc',
        'url_request/url_request_job_manager.h',
        'url_request/url_request_job_metrics.cc',
        'url_request/url_request_job_metrics.h',
        'url_request/url_request_job_tracker.cc',
        'url_request/url_request_job_tracker.h',
        'url_request/url_request_simple_job.cc',
        'url_request/url_request_simple_job.h',
        'url_request/url_request_status.h',
        'url_request/url_request_test_job.cc',
        'url_request/url_request_test_job.h',
        'url_request/url_request_view_cache_job.cc',
        'url_request/url_request_view_cache_job.h',
        'http/http_atom_list.h',
        'http/http_cache.cc',
        'http/http_cache.h',
        'http/http_chunked_decoder.cc',
        'http/http_chunked_decoder.h',
        'http/http_network_layer.cc',
        'http/http_network_layer.h',
        'http/http_network_session.h',
        'http/http_network_transaction.cc',
        'http/http_network_transaction.h',
        'http/http_request_info.h',
        'http/http_response_headers.cc',
        'http/http_response_headers.h',
        'http/http_response_info.h',
        'http/http_transaction.h',
        'http/http_transaction_factory.h',
        'http/http_util.cc',
        'http/http_util.h',
        'http/http_auth.cc',
        'http/http_auth.h',
        'http/http_auth_cache.cc',
        'http/http_auth_cache.h',
        'http/http_auth_handler.h',
        'http/http_auth_handler.cc',
        'http/http_auth_handler_basic.cc',
        'http/http_auth_handler_basic.h',
        'http/http_auth_handler_digest.cc',
        'http/http_auth_handler_digest.h',
        'http/http_auth.cc',
        'http/http_auth.h',
        'http/http_auth_handler.h',
        'http/http_auth_handler.cc',
        'http/http_auth_handler_basic.cc',
        'http/http_auth_handler_basic.h',
        'http/http_auth_handler_digest.cc',
        'http/http_auth_handler_digest.h',
        'http/http_vary_data.cc',
        'http/http_vary_data.h',
        'disk_cache/addr.h',
        'disk_cache/backend_impl.cc',
        'disk_cache/backend_impl.h',
        'disk_cache/block_files.cc',
        'disk_cache/block_files.h',
        'disk_cache/cache_util.h',
        'disk_cache/cache_util_win.cc',
        'disk_cache/disk_cache.h',
        'disk_cache/disk_format.h',
        'disk_cache/entry_impl.cc',
        'disk_cache/entry_impl.h',
        'disk_cache/errors.h',
        'disk_cache/eviction.cc',
        'disk_cache/eviction.h',
        'disk_cache/file.h',
        'disk_cache/file_block.h',
        'disk_cache/file_lock.cc',
        'disk_cache/file_lock.h',
        'disk_cache/file_win.cc',
        'disk_cache/hash.cc',
        'disk_cache/hash.h',
        'disk_cache/mapped_file.h',
        'disk_cache/mapped_file_win.cc',
        'disk_cache/mem_backend_impl.cc',
        'disk_cache/mem_backend_impl.h',
        'disk_cache/mem_entry_impl.cc',
        'disk_cache/mem_entry_impl.h',
        'disk_cache/mem_rankings.cc',
        'disk_cache/mem_rankings.h',
        'disk_cache/rankings.cc',
        'disk_cache/rankings.h',
        'disk_cache/stats.cc',
        'disk_cache/stats.h',
        'disk_cache/stats_histogram.cc',
        'disk_cache/stats_histogram.h',
        'disk_cache/storage_block-inl.h',
        'disk_cache/storage_block.h',
        'disk_cache/trace.cc',
        'disk_cache/trace.h',
        'proxy/proxy_config_service_fixed.h',
        'proxy/proxy_config_service_win.cc',
        'proxy/proxy_config_service_win.h',
        'proxy/proxy_resolver_winhttp.cc',
        'proxy/proxy_resolver_winhttp.h',
        'proxy/proxy_script_fetcher.cc',
        'proxy/proxy_script_fetcher.h',
        'proxy/proxy_service.cc',
        'proxy/proxy_service.h',
        'ftp/ftp_auth_cache.cc',
        'ftp/ftp_auth_cache.h',
        'ftp/ftp_network_layer.cc',
        'ftp/ftp_network_layer.h',
        'ftp/ftp_network_session.h',
        'ftp/ftp_network_transaction.cc',
        'ftp/ftp_network_transaction.h',
        'ftp/ftp_request_info.h',
        'ftp/ftp_response_info.h',
        'ftp/ftp_transaction.h',
        'ftp/ftp_transaction_factory.h',
      ],
      'conditions': [
        [ 'OS != "win"', {
            'sources!': [
              'base/file_stream_win.cc',
              'base/net_util_win.cc',
              'base/platform_mime_util_win.cc',
              'base/ssl_client_socket_win.cc',
              'base/ssl_config_service.cc',
              'base/tcp_client_socket_win.cc',
              'base/wininet_util.cc',
              'base/winsock_init.cc',
              'base/x509_certificate_win.cc',
              'build/precompiled_net.cc',
              'disk_cache/cache_util_win.cc',
              'disk_cache/file_win.cc',
              'disk_cache/mapped_file_win.cc',
              'proxy/proxy_config_service_win.cc',
              'proxy/proxy_resolver_winhttp.cc',
              'url_request/url_request_ftp_job.cc',
              'url_request/url_request_inet_job.cc',
            ],
            'sources': [
              'base/file_stream_posix.cc',
              'base/net_util_posix.cc',
              'base/tcp_client_socket_libevent.cc',
              'disk_cache/cache_util_posix.cc',
              'disk_cache/file_posix.cc',
              'disk_cache/mapped_file_posix.cc',
            ],
          },
        ],
        [ 'OS == "linux"', {
            'sources': [
              'base/nss_memio.c',
              # TODO(tc): gnome-vfs? xdgmime? /etc/mime.types?
              'base/platform_mime_util_linux.cc',
              'base/ssl_client_socket_nss.cc',
              'base/x509_certificate_nss.cc',
            ],
          },
        ],
        [ 'OS == "mac"', {
            'sources': [
              'base/platform_mime_util_mac.cc',
              'base/ssl_client_socket_mac.cc',
              'base/x509_certificate_mac.cc',
              'proxy/proxy_resolver_mac.cc',
            ],
          },
        ],
      ],
    },
    {
      'target_name': 'net_resources',
      'type': 'none',
      'sources': [
        'net_resources.grd',
        'net_resources.h',
      ],
      'vs_postbuild':
        '$(ProjectDir)..\\tools\\grit\\build\\grit_resource_file.bat '
        '$(ProjectDir)base\\net_resources.grd '
        '$(ProjectDir) '
        '$(OutDir)\\grit_derived_sources',
    },
    {
      'target_name': 'net_unittests',
      'type': 'executable',
      'dependencies': [
        'net',
        '../base/base.gyp:base',
        '../testing/gtest.gyp:gtest',
      ],
      'sources': [
        'build/precompiled_net.h',
        'base/run_all_unittests.cc',
        'disk_cache/addr_unittest.cc',
        'disk_cache/backend_unittest.cc',
        'disk_cache/block_files_unittest.cc',
        'disk_cache/disk_cache_test_base.cc',
        'disk_cache/disk_cache_test_base.h',
        'disk_cache/disk_cache_test_util.cc',
        'disk_cache/disk_cache_test_util.h',
        'disk_cache/entry_unittest.cc',
        'disk_cache/mapped_file_unittest.cc',
        'disk_cache/storage_block_unittest.cc',
        'http/http_auth_cache_unittest.cc',
        'http/http_auth_handler_basic_unittest.cc',
        'http/http_auth_handler_digest_unittest.cc',
        'http/http_auth_unittest.cc',
        'http/http_cache_unittest.cc',
        'http/http_chunked_decoder_unittest.cc',
        'http/http_network_layer_unittest.cc',
        'http/http_network_transaction_unittest.cc',
        'http/http_response_headers_unittest.cc',
        'http/http_transaction_unittest.cc',
        'http/http_transaction_unittest.h',
        'http/http_util_unittest.cc',
        'http/http_vary_data_unittest.cc',
        'base/base64_unittest.cc',
        'base/bzip2_filter_unittest.cc',
        'base/client_socket_pool_unittest.cc',
        'base/cookie_monster_unittest.cc',
        'base/cookie_policy_unittest.cc',
        'base/data_url_unittest.cc',
        'base/directory_lister_unittest.cc',
        'base/escape_unittest.cc',
        'base/file_stream_unittest.cc',
        'base/filter_unittest.cc',
        'base/gzip_filter_unittest.cc',
        'base/host_resolver_unittest.cc',
        'base/listen_socket_unittest.cc',
        'base/listen_socket_unittest.h',
        'base/mime_sniffer_unittest.cc',
        'base/mime_util_unittest.cc',
        'base/net_util_unittest.cc',
        'base/registry_controlled_domain_unittest.cc',
        'base/sdch_filter_unittest.cc',
        'base/ssl_client_socket_unittest.cc',
        'base/ssl_config_service_unittest.cc',
        'base/tcp_client_socket_unittest.cc',
        'base/telnet_server_unittest.cc',
        'base/test_completion_callback_unittest.cc',
        'base/wininet_util_unittest.cc',
        'base/x509_certificate_unittest.cc',
        'ftp/ftp_auth_cache_unittest.cc',
        'url_request/url_request_unittest.cc',
        'url_request/url_request_unittest.h',
        'proxy/proxy_script_fetcher_unittest.cc',
        'proxy/proxy_service_unittest.cc',
      ],
      'conditions': [
        [ 'OS != "win"', {
            'sources!': [
              'base/wininet_util_unittest.cc',
            ],
          },
        ],
        [ 'OS == "linux"', {
            'sources!': [
              'base/sdch_filter_unittest.cc',
              'base/ssl_config_service_unittest.cc',
            ],
          },
        ],
        [ 'OS == "mac"', {
            'sources!': [
              'base/x509_certificate_unittest.cc',
              'base/sdch_filter_unittest.cc',
              'base/ssl_config_service_unittest.cc',
              'url_request/url_request_unittest.cc',
            ],
            'sources': [
              '../base/platform_test_mac.cc',
            ],
          },
        ],
        # This is needed to trigger the dll copy step on windows.
        [ 'OS == "win"', {
            'dependencies': [
              '../third_party/icu38/icu38.gyp:icudata',
            ],
          },
        ],
      ],
    },
  ],
}
